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
        self.VERIFICATION_CODE = verification_code
        self.set_option('MerchantID', merchant_id)

        self._products = []

        if not testing:
            self.ENDPOINT = 'https://paymentweb.valitor.is'

    def format_url(self, path):
        return "{}{}".format(self.ENDPOINT, path)
    
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
            result["Product_{}_Quantity".format(i+1)] = str(product['Quantity'])
            result["Product_{}_Price".format(i+1)] = str(product['Price'])
            result["Product_{}_Discount".format(i+1)] = str(product['Discount'])
            result["Product_{}_Description".format(i+1)] = str(product['Description'])
        return result
            

    def generate_signature(self):
        m = hashlib.sha256()
        m.update(str(self.VERIFICATION_CODE).encode('utf-8'))
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

    def verify_signature(self, reference_number, signature_response):
        m = hashlib.sha256()
        m.update(self.VERIFICATION_CODE.encode('utf-8'))
        m.update(reference_number.encode('utf-8'))
        signature = m.hexdigest()

        return signature == signature_response

    def build_form_html(self, button_text="Pay", button_classes=""):
        options = ""
        for key, value in self.options.items():
            options += "                <input type=\"hidden\" id=\"{}\" name=\"{}\" value=\"{}\" />\n".format(key, key, value)
        for key, value in self.products_flat.items():
            options += "                <input type=\"hidden\" id=\"{}\" name=\"{}\" value=\"{}\" />\n".format(key, key, value)

        if button_classes:
            button_classes = " class=\"{}\"".format(button_classes)
        
        form = """
            <form action="{}" method="POST">
                <input type="hidden" id="DigitalSignature" name="DigitalSignature" value="{}" />
{}
                <button type="submit"{}>{}</button>
            </form>
        """.format(self.ENDPOINT, self.generate_signature(), options, button_classes, button_text)

        return form