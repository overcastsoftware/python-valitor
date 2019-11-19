# -*- coding: utf-8 -*-

import os
import uuid
from .context import valitor_python

import unittest
import pytest
from random import randint






@pytest.fixture
def credentials():
    merchant_id = os.getenv('VALITOR_PAYMENTPAGE_MERCHANT_ID', None)
    verification_code = os.getenv('VALITOR_PAYMENTPAGE_VERIFICATION_CODE', None)
    
    return {
        'merchant_id': merchant_id,
        'verification_code': verification_code,
    }



@pytest.fixture
def credentials_docs():
    
    return {
        'merchant_id': '207',
        'verification_code': '2ef8ec654c',
    }


@pytest.fixture
def valitor(credentials):
    return valitor_python.ValitorPaymentPageClient(**credentials)


@pytest.fixture
def valitor_docs(credentials_docs):
    return valitor_python.ValitorPaymentPageClient(**credentials_docs)



@pytest.fixture
def valitor_docs_products():
    return [{
        'Quantity': 2,
        'Price': 1500,
        'Discount': 0,
        'Description': 'Product 1'
    }, {
        'Quantity': 1,
        'Price': 1000,
        'Discount': 0,
        'Description': 'Product 2'
    }]

@pytest.fixture
def valitor_docs_with_products(credentials_docs, valitor_docs_products):
    client = valitor_python.ValitorPaymentPageClient(**credentials_docs)
    client.add_product(valitor_docs_products[0])
    client.add_product(valitor_docs_products[1])
    return client


@pytest.fixture
def valitor_with_products(credentials, valitor_docs_products):
    client = valitor_python.ValitorPaymentPageClient(**credentials)
    client.add_product(valitor_docs_products[0])
    client.add_product(valitor_docs_products[1])
    return client


@pytest.mark.valitorpaymentpage
def test_can_init_client(credentials):
    valitor = valitor_python.ValitorPaymentPageClient(**credentials)


@pytest.mark.valitorpaymentpage
def test_docs_example_hash(valitor_docs_with_products):
    

    valitor_docs_with_products.set_option('ReferenceNumber', '456')
    valitor_docs_with_products.set_option('PaymentSuccessfulURL', 'http://www.minsida.is/takkfyrir')
    valitor_docs_with_products.set_option('PaymentSuccessfulServerSideURL', 'http://www.minsida.is/sale.aspx?c=8282&ref=232')

    signature = valitor_docs_with_products.generate_signature()
    assert signature == '8573f2a43f4d5fed99aaee4c8d098f14903afaf709ea1e0e7840e5e56edd962a'



@pytest.mark.valitorpaymentpage
def test_form(valitor_docs_with_products):
    

    valitor_docs_with_products.set_option('ReferenceNumber', uuid.uuid4())
    valitor_docs_with_products.set_option('PaymentSuccessfulURL', 'http://www.minsida.is/takkfyrir')
    valitor_docs_with_products.set_option('PaymentSuccessfulServerSideURL', 'http://www.minsida.is/sale.aspx?c=8282&ref=232')

    html = valitor_docs_with_products.build_form_html()
    
    assert "name=\"PaymentSuccessfulURL\" value=\"http://www.minsida.is/takkfyrir\"" in html
    assert "name=\"Product_1_Price\" value=\"1500\"" in html


@pytest.mark.valitorpaymentpage
def test_form_with_button_classes(valitor_with_products):
    

    valitor_with_products.set_option('ReferenceNumber', uuid.uuid4())
    valitor_with_products.set_option('DisplayBuyerInfo', 1)
    valitor_with_products.set_option('PaymentSuccessfulURLText', 'Til baka')
    valitor_with_products.set_option('PaymentSuccessfulURL', 'http://www.mbl.is')
    valitor_with_products.set_option('PaymentSuccessfulServerSideURL', 'http://www.mbl.is')

    html = valitor_with_products.build_form_html(button_classes="btn btn-primary")
    print(html)
    assert "class=\"btn btn-primary\"" in html



@pytest.mark.valitorpaymentpage
def test_sha():
    import hashlib
    m = hashlib.sha256()
    m.update("abc".encode('utf-8'))
    assert m.hexdigest() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"