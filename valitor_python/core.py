# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from zeep import Client, Settings
from zeep.wsse.username import UsernameToken
from lxml import etree
from .errors import ValitorException
import uuid


class ValitorClient(object):
    
    USERNAME = ''
    PASSWORD = ''
    CONTRACT_NUMBER = ''
    CONTRACT_ID = ''
    POSI_ID = ''
    ENDPOINT = 'https://api.processing.uat.valitor.com/Fyrirtaekjagreidslur/Fyrirtaekjagreidslur.asmx'
    ENDPOINT_PAYMENT = 'https://api.processing.uat.valitor.com/Fyrirtaekjagreidslur/Libra.asmx'

    def __init__(self, username, password, contract_number, contract_id, posi_id, testing=True):
        self.USERNAME = username
        self.PASSWORD = password
        self.CONTRACT_NUMBER = contract_number
        self.CONTRACT_ID = contract_id
        self.POSI_ID = posi_id
        self.TESTING = testing

        if not testing:
            self.ENDPOINT = 'https://api.processing.valitor.com/Fyrirtaekjagreidslur/Fyrirtaekjagreidslur.asmx'
            self.ENDPOINT_PAYMENT = 'https://api.processing.valitor.com/Fyrirtaekjagreidslur/Libra.asmx'

        self.WSDL = "{}?WSDL".format(self.ENDPOINT)
        self.WSDL_PAYMENT = "{}?WSDL".format(self.ENDPOINT_PAYMENT)

        #settings = Settings(xml_huge_tree=True, raw_response=True)
        #self.client = Client(self.WSDL, settings=settings)
        
        self.client = Client(self.WSDL)
        self.client_payment = Client(self.WSDL_PAYMENT)


    def check_error(self, response):
        if response['Villunumer'] != 0:
            raise ValitorException(response['Villunumer'], response['Villuskilabod'], response['VilluLogID'])

    @classmethod
    def currency_code_numeric(cls, code):

        currency_codes = {
            'USD': 840,
            'ISK': 352,
            'EUR': 978,
        }

        return currency_codes[code]
        
    
    def FaSyndarkortnumer(self, card_number, valid_until_year, valid_until_month, cvv):
        response = self.client.service.FaSyndarkortnumer(
            Notandanafn=self.USERNAME,
            Lykilord=self.PASSWORD,
            Samningsnumer=self.CONTRACT_NUMBER,
            SamningsKennitala=self.CONTRACT_ID,
            PosiID=self.POSI_ID,
            Kortnumer=card_number,
            Gildistimi="{}{}".format(valid_until_month, valid_until_year),
            Oryggisnumer=cvv,
            Stillingar=''
        )

        self.check_error(response)

        return response['Syndarkortnumer']


    def FaSidustuFjoraIKortnumeriUtFraSyndarkortnumeri(self, card_number_virtual):
        response = self.client.service.FaSidustuFjoraIKortnumeriUtFraSyndarkortnumeri(
            Notandanafn=self.USERNAME,
            Lykilord=self.PASSWORD,
            SamningsKennitala=self.CONTRACT_ID,
            Syndarkortnumer=card_number_virtual,
            Stillingar=''
        )
            
        self.check_error(response)

        return response['Kortnumer']


    def FaHeimild(self, card_number_virtual, amount, currency='ISK'):
        response = self.client.service.FaHeimild(
            Notandanafn=self.USERNAME,
            Lykilord=self.PASSWORD,
            Samningsnumer=self.CONTRACT_NUMBER,
            SamningsKennitala=self.CONTRACT_ID,
            PosiID=self.POSI_ID,
            Syndarkortnumer=card_number_virtual,
            Upphaed=amount,
            Gjaldmidill=currency,
            Stillingar=''
        )
            
        self.check_error(response)

        return response['Kvittun']

