# -*- coding: utf-8 -*-

from .context import valitor_python

import unittest
import pytest

@pytest.fixture
def credentials():
    import os
    username = os.getenv('VALITOR_TEST_USERNAME', None)
    password = os.getenv('VALITOR_TEST_PASSWORD', None)
    contract_number = os.getenv('VALITOR_TEST_CONTRACT_NUMBER', None)
    posi_id = os.getenv('VALITOR_TEST_POSI_ID', None)
    
    return {
        'username': username,
        'password': password,
        'contract_number': contract_number,
        'posi_id': posi_id,
    }

@pytest.fixture
def client(credentials):
    return valitor_python.ValitorClient(**credentials)

def test_can_init_client(credentials):
    valitor = valitor_python.ValitorClient(**credentials)

def test_fa_syndarnumer(client):
    assert True==False
