# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from zeep import Client, Settings
from zeep.wsse.username import UsernameToken
from lxml import etree


class ValitorClient(object):
    
    USERNAME = ''
    PASSWORD = ''
    CONTRACT_NUMBER = ''
    POSI_ID = ''
    ENDPOINT = 'https://api.processing.uat.valitor.com/Fyrirtaekjagreidslur/Fyrirtaekjagreidslur.asmx'
    

    def __init__(self, username, password, contract_number, posi_id, testing=True):
        self.USERNAME = username
        self.PASSWORD = password
        self.CONTRACT_NUMBER = contract_number
        self.POSI_ID = posi_id
        self.TESTING = testing

        if not testing:
            self.ENDPOINT = 'https://api.processing.valitor.com/Fyrirtaekjagreidslur/Fyrirtaekjagreidslur.asmx'

        self.WSDL = "{}?WSDL".format(self.ENDPOINT)

        settings = Settings(xml_huge_tree=True, raw_response=True)

        self.client = Client(self.WSDL, settings=settings)
        