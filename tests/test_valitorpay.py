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
def verification_data():
    return {
        "cardholderAuthenticationVerificationData": "hq6EHIP0PfZEYwAAnuCpB4MAAAA=",
        "mdStatus": 4,
        "transactionXid": "nrQGVcVW0CIzw6wsqwIlxLAUTCE="
    }


def test_can_init_client(credentials):
    valitor = valitor_python.ValitorPayClient(**credentials)


def test_create_virtual_card(valitor, creditcard, verification_data):

    response = valitor.CreateVirtualCard(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], cardVerificationData=verification_data)

    assert response['isSuccess'] == True
    assert 'virtualCard' in response.keys()
    

def test_create_virtual_card_without_verification_data_raises_exception(valitor, creditcard, verification_data):

    with pytest.raises(valitor_python.ValitorPayException) as exc_info:
        response = valitor.CreateVirtualCard(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvc'], cardVerificationData=None)

    