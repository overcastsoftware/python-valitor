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
def valitor_v2(credentials):
    options = {'apiversion': '2.0'}
    options.update(**credentials)
    return valitor_python.ValitorPayClient(**options)

@pytest.fixture
def wrong_credentials():
    return {
        'apikey': "DummyApiKey"
    }

@pytest.fixture
def wrong_valitor(wrong_credentials):
    return valitor_python.ValitorPayClient(**wrong_credentials)


@pytest.fixture
def verification_data():
    return {
        "cardholderAuthenticationVerificationData": "jq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "transactionXid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE=",
    }


@pytest.fixture
def verification_data_v2():
    return {
        "cavv": "jq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "xid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE=",
    }


@pytest.fixture
def verification_data_payment():
    return {
        "cardholderAuthenticationVerificationData": "jq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "transactionXid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE=",
        "mdStatus": "1",
    }


@pytest.fixture
def verification_data_payment_v2():
    return {
        "cavv": "jq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "xid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE=",
        "mdStatus": "1",
    }

@pytest.fixture
def verification_data_payment_transid_v2():
    return {
        "cavv": "jq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "xid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE=",
        "mdStatus": "1",
        "dsTransId": None
    }



@pytest.mark.valitorpay
def test_can_init_client(credentials):
    valitor = valitor_python.ValitorPayClient(**credentials)


@pytest.mark.valitorpay
def test_card_verification(valitor, creditcard):

    response = valitor.CardVerification(creditcard['number'], creditcard['year'], creditcard['month'], 0, 'ISK', 'http://acme.com/success', 'http://acme.com/failed', merchantData='reference-1000')

    assert 'cavv' in response
    assert 'xid' in response

@pytest.mark.valitorpay
def test_card_verification_json(valitor, creditcard):

    response = valitor.CardVerification(creditcard['number'], creditcard['year'], creditcard['month'], 0, 'ISK', 'http://acme.com/success', 'http://acme.com/failed', merchantData='reference-1000', threeDeeSecureResponseType=valitor.ThreeDeeSecureResponseType.JSON)

    assert 'postUrl' in response.keys()
    assert 'verificationFields' in response.keys()


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
def test_card_payment(valitor, creditcard, verification_data_payment):
    response = valitor.CardPayment(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], 100, "ISK", valitor.CardOperation.Sale, valitor.TransactionType.ECommerce, cardVerificationData=verification_data_payment)
    assert response["isSuccess"] == True


@pytest.mark.valitorpay
def test_virtual_card_payment(valitor, creditcard, verification_data):
    response = valitor.VirtualCardPayment(creditcard['virtual'], 100, "ISK", valitor.VirtualCardOperation.Sale)
    assert response["isSuccess"] == True

@pytest.mark.valitorpay
def test_create_virtual_card_v2(valitor_v2, creditcard, verification_data_v2):

    response = valitor_v2.CreateVirtualCard(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], cardVerificationData=verification_data_v2)

    assert response['isSuccess'] == True
    assert 'virtualCard' in response.keys()

@pytest.mark.valitorpay
def test_card_payment_v2(valitor_v2, creditcard, verification_data_payment_v2):
    response = valitor_v2.CardPayment(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], 100, "ISK", valitor_v2.CardOperation.Sale, valitor_v2.TransactionType.ECommerce, cardVerificationData=verification_data_payment_v2)
    assert response["isSuccess"] == True

@pytest.mark.valitorpay
def test_virtual_card_payment_v2(valitor_v2, creditcard, verification_data_v2):
    response = valitor_v2.VirtualCardPayment(creditcard['virtual'], 100, "ISK", valitor_v2.VirtualCardOperation.Sale)
    assert response["isSuccess"] == True

@pytest.mark.valitorpay
def test_card_payment_transid_v2(valitor_v2, creditcard, verification_data_payment_transid_v2):
    response = valitor_v2.CardPayment(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], 100, "ISK", valitor_v2.CardOperation.Sale, valitor_v2.TransactionType.ECommerce, cardVerificationData=verification_data_payment_transid_v2)
    print(response)
    assert response["isSuccess"] == True
