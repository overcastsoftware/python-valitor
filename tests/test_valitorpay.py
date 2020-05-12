# -*- coding: utf-8 -*-

import os

from .context import valitor_python

import unittest
import pytest
from random import randint




@pytest.fixture
def creditcard():
    """
    test card  should be in ENV variable VALITOR_TEST_CARD and contain information about the 
    card formatted as such:

        VALITORPAY_TEST_CARD=number:<card number>,month:<month>,year:<year>,cvv:<CVV code>

    """
    testcard = os.getenv('VALITORPAY_TEST_CARD', None)
    card = dict(map(lambda k: k.split(':'), testcard.split(",")))
    return card


@pytest.fixture
def credentials():
    apikey = os.getenv('VALITORPAY_APIKEY', None)
    
    return {
        'apikey': apikey,
    }

@pytest.fixture
def valitor(credentials):
    return valitor_python.ValitorPayClient(**credentials)



@pytest.fixture
def wrong_credentials():
    return {
        'apikey': "ApiKeyUAT.RxE3xfVnksfC/UnoDpu31UQ/gY"
    }

@pytest.fixture
def wrong_valitor(wrong_credentials):
    return valitor_python.ValitorPayClient(**wrong_credentials)

@pytest.fixture
def verification_data():
    return {
        "cardholderAuthenticationVerificationData": "hq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "mdStatus": 4,
        "transactionXid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE="
    }


@pytest.mark.valitorpay
def test_can_init_client(credentials):
    valitor = valitor_python.ValitorPayClient(**credentials)


@pytest.mark.valitorpay
def test_create_virtual_card(valitor, creditcard, verification_data):

    response = valitor.CreateVirtualCard(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], cardVerificationData=verification_data)

    assert response['isSuccess'] == True
    assert 'virtualCard' in response.keys()


@pytest.mark.valitorpay
def test_create_virtual_card_without_credentials_raises_exception(wrong_valitor, creditcard, verification_data):

    with pytest.raises(valitor_python.ValitorPayException) as exc_info:
        response = wrong_valitor.CreateVirtualCard(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], cardVerificationData=None)

@pytest.mark.valitorpay
def test_create_virtual_card_without_verification_data_raises_exception(valitor, creditcard, verification_data):

    with pytest.raises(valitor_python.ValitorPayException) as exc_info:
        response = valitor.CreateVirtualCard(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], cardVerificationData=None)


@pytest.mark.valitorpay
def test_card_payment(valitor, creditcard, verification_data):

    response = valitor.CardPayment(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], valitor.CardOperation.Sale, valitor.TransactionType.ECommerce, "ISK", 100, cardVerificationData=verification_data)
    print(response)


@pytest.mark.valitorpay
def test_virtual_card_payment(valitor, creditcard, verification_data):

    response = valitor.VirtualCardPayment(creditcard['virtual'], "ISK", 100, valitor.VirtualCardOperation.Sale)
    print(response)

