# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from .errors import ValitorPayException
import uuid
from enum import Enum
import requests
import hashlib



class ValitorPaymentPageClient(object):

    MERCHANT_ID = ''
    VERIFICATION_CODE = ''
    ENDPOINT = 'https://paymentweb.uat.valitor.is'


    options = {
        'AuthorizationOnly': '0',
        'ReferenceNumber': '',
        'PaymentSuccessfulURL': '',
        'PaymentSuccessfulServerSideURL': '',
        'Currency': 'ISK',
    }


    def __init__(self, merchant_id, verification_code, testing=True):
        self.TESTING = testing

        self.set_option('MerchantID', merchant_id)
        self.set_option('VerificationCode', verification_code)

        self._products = []

        if not testing:
            self.ENDPOINT = 'https://paymentweb.valitor.is'

    def format_url(self, path):
        return f"{self.ENDPOINT}{path}"
    
    def set_option(self, key, value):
        self.options[key] = str(value)
    
    def add_product(self, product):
        assert 'Quantity' in product.keys()
        assert 'Price' in product.keys()
        assert 'Description' in product.keys()
        assert 'Discount' in product.keys()
        self._products.append({
            'Quantity': str(product['Quantity']),
            'Price': str(product['Price']),
            'Description': str(product['Description']),
            'Discount': str(product['Discount']),
        })

    @property
    def products_flat(self):
        result = {}
        for i, product in enumerate(self._products):
            result[f"Product_{i+1}_Quantity"] = str(product['Quantity'])
            result[f"Product_{i+1}_Price"] = str(product['Price'])
            result[f"Product_{i+1}_Discount"] = str(product['Discount'])
            result[f"Product_{i+1}_Description"] = str(product['Description'])
        return result
            

    def generate_signature(self):
        m = hashlib.sha256()
        m.update(self.options['VerificationCode'].encode('utf-8'))
        m.update(self.options['AuthorizationOnly'].encode('utf-8'))
        for product in self._products:
            m.update(product['Quantity'].encode('utf-8'))
            m.update(product['Price'].encode('utf-8'))
            m.update(product['Discount'].encode('utf-8'))
        m.update(self.options['MerchantID'].encode('utf-8'))
        m.update(self.options['ReferenceNumber'].encode('utf-8'))
        m.update(self.options['PaymentSuccessfulURL'].encode('utf-8'))
        m.update(self.options['PaymentSuccessfulServerSideURL'].encode('utf-8'))
        m.update(self.options['Currency'].encode('utf-8'))
        
        return m.hexdigest()

    def build_form_html(self, button_classes=""):
        options = ""
        for key, value in self.options.items():
            options += f"                <input type=\"hidden\" id=\"{key}\" name=\"{key}\" value=\"{value}\" />\n"
        for key, value in self.products_flat.items():
            options += f"                <input type=\"hidden\" id=\"{key}\" name=\"{key}\" value=\"{value}\" />\n"

        if button_classes:
            button_classes = f" class=\"{button_classes}\""
        
        form = f"""
            <form action="{self.ENDPOINT}" method="POST">
                <input type="hidden" id="DigitalSignature" name="DigitalSignature" value="{self.generate_signature()}" />
{options}
                <button type="submit"{button_classes}>Greiða</button>
            </form>
        """

        return form