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

        VALITOR_TEST_CARD=number:<card number>,month:<month>,year:<year>,cvv:<CVV code>,virtual:<expected virtual card number>

    """
    testcard = os.getenv('VALITOR_TEST_CARD', None)
    card = dict(map(lambda k: k.split(':'), testcard.split(",")))
    return card


@pytest.fixture
def credentials():
    username = os.getenv('VALITOR_TEST_USERNAME', None)
    password = os.getenv('VALITOR_TEST_PASSWORD', None)
    contract_number = os.getenv('VALITOR_TEST_CONTRACT_NUMBER', None)
    contract_id = os.getenv('VALITOR_TEST_CONTRACT_ID', None)
    posi_id = os.getenv('VALITOR_TEST_POSI_ID', None)
    
    return {
        'username': username,
        'password': password,
        'contract_number': contract_number,
        'contract_id': contract_id,
        'posi_id': posi_id,
        #'testing': False,
    }


@pytest.fixture
def valitor(credentials):
    return valitor_python.ValitorClient(**credentials)


@pytest.mark.valitor
def test_can_init_client(credentials):
    valitor = valitor_python.ValitorClient(**credentials)


@pytest.mark.valitor
def test_fa_syndarnumer(valitor, creditcard):

    response = valitor.FaSyndarkortnumer(creditcard['number'], creditcard['year'], creditcard['month'], creditcard['cvv'])

    assert response == creditcard['virtual']


@pytest.mark.valitor
def test_fa_syndarnumer_with_invalid_expiration_raises_exception(valitor, creditcard):
    with pytest.raises(valitor_python.ValitorException) as exc_info:
        response = valitor.FaSyndarkortnumer(creditcard['number'], '00', '00', creditcard['cvv'])

    assert exc_info.value.number == 232


@pytest.mark.valitor
def test_fa_sidustu_fjora_fra_syndarnumeri(valitor, creditcard):
    response = valitor.FaSidustuFjoraIKortnumeriUtFraSyndarkortnumeri(creditcard['virtual'])
    
    assert response == creditcard['number'][-4:]


@pytest.mark.valitor
def test_fa_sidustu_fjora_fra_syndarnumeri_with_invalid_card_raises_exception(valitor):
    with pytest.raises(valitor_python.ValitorException) as exc_info:
        response = valitor.FaSidustuFjoraIKortnumeriUtFraSyndarkortnumeri('5999991234567890')
    
    assert exc_info.value.number == 220


@pytest.mark.valitor
def test_fa_heimild(valitor, creditcard):
    amount = '2990'
    response = valitor.FaHeimild(creditcard['virtual'], amount, 'ISK')
    
    assert response['Upphaed'] == amount
    assert response['Kortnumer'][-4:] == creditcard['number'][-4:]


@pytest.mark.valitor
def test_fa_heimild_with_invalid_card_raises_exception(valitor, creditcard):
    amount = '2990'

    with pytest.raises(valitor_python.ValitorException) as exc_info:
        response = valitor.FaHeimild('5123456789123456', amount, 'ISK')
    
    assert exc_info.value.number == 220

@pytest.mark.valitor
def test_fa_heimild_with_invalid_currency_raises_exception(valitor, creditcard):
    amount = '2990'

    with pytest.raises(valitor_python.ValitorException) as exc_info:
        response = valitor.FaHeimild(creditcard['virtual'], amount, 'USD')
    
    assert exc_info.value.number == 999

@pytest.mark.valitor
def test_fa_endurgreitt(valitor, creditcard):
    amount = '2990'
    response = valitor.FaEndurgreitt(creditcard['virtual'], amount, 'ISK')
    
    assert response['Upphaed'] == amount
    assert response['Kortnumer'][-4:] == creditcard['number'][-4:]


@pytest.mark.valitor
def test_uppfaera_gildistima_with_invalid_year(valitor, creditcard):

    with pytest.raises(valitor_python.ValitorException) as exc_info:
        response = valitor.UppfaeraGildistima(creditcard['virtual'], '05', '23')
    

    assert exc_info.value.number == 232


@pytest.mark.valitor
def test_uppfaera_gildistima(valitor, creditcard):

    response = valitor.UppfaeraGildistima(creditcard['virtual'], '23', '05')
