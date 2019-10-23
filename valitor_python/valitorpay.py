# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from .errors import ValitorPayException
import uuid
from enum import Enum
import requests


class CardVerificationData(object):

    class MdStatusTypes(Enum):
        MdFullyAuthenticated = 1
        MdNotEnrolled = 2
        MdAttempt = 3
        MdUReceived = 4

        @classmethod
        def is_valid_status_type(self, status_type):
            try:
                CardVerificationData.MdStatusTypes(status_type)
                return True
            except ValueError:
                return False

    def __init__(self, cardholderAuthenticationVerificationData, mdStatus, transactionXid):
        assert CardVerificationData.MdStatusTypes.is_valid_status_type(mdStatus)
        self.data = {
            'cardholderAuthenticationVerificationData': cardholderAuthenticationVerificationData,
            'mdStatus': mdStatus,
            'transactionXid': transactionXid,
        }


class ValitorPayClient(object):
    
    APIKEY = ''
    ENDPOINT = 'https://uat.valitorpay.com'


    def format_url(self, path):
        return f"{self.ENDPOINT}{path}"

    def check_error(self, response):
        if response.status_code == 400:
            errors = response.json()
            output = ""
            for k, v in errors.items():
                vv = ", ".join(f"{x}" for x in v)
                output += f"{k}: {vv}"
            raise ValitorPayException(output)


    class SubsequentTransactionTypes(Enum):

        CardholderInitiatedCredentialOnFile = 'CardholderInitiatedCredentialOnFile'
        MerchantInitiatedCredentialOnFile = 'MerchantInitiatedCredentialOnFile'
        MerchantInitiatedRecurring = 'MerchantInitiatedRecurring'
        MerchantInitiatedInstallment = 'MerchantInitiatedInstallment'
        MerchantInitiatedIncremental = 'MerchantInitiatedIncremental'
        MerchantInitiatedResubmission = 'MerchantInitiatedResubmission'
        MerchantInitiatedDelayedCharges = 'MerchantInitiatedDelayedCharges'
        MerchantInitiatedReauthorization = 'MerchantInitiatedReauthorization'
        MerchantInitiatedNoShow = 'MerchantInitiatedNoShow'


    def __init__(self, apikey, testing=True):
        self.APIKEY = apikey
        self.TESTING = testing

        if not testing:
            self.ENDPOINT = 'https://api.processing.valitor.com/Fyrirtaekjagreidslur/Fyrirtaekjagreidslur.asmx'


    def CreateVirtualCard(self, cardNumber, expirationYear, expirationMonth, cvc, subsequentTransactionType=SubsequentTransactionTypes.CardholderInitiatedCredentialOnFile.value, cardVerificationData=None):

        payload = {
            "cardNumber": cardNumber,
            "expirationMonth": expirationMonth,
            "expirationYear": expirationYear,
            "cvc": cvc,
            "subsequentTransactionType": subsequentTransactionType,
        }        

        if cardVerificationData:
            cv_data = CardVerificationData(**cardVerificationData)
            assert "cardholderAuthenticationVerificationData" in cardVerificationData
            payload["cardVerificationData"] = cardVerificationData

        response = requests.post(self.format_url("/VirtualCard/CreateVirtualCard"), json=payload, auth=(self.APIKEY, ''))

        self.check_error(response)

        return response.json()


    # def check_error(self, response):
    #     if response['Villunumer'] != 0:
    #         raise ValitorException(response['Villunumer'], response['Villuskilabod'], response['VilluLogID'])

    
    # def FaSyndarkortnumer(self, card_number, valid_until_year, valid_until_month, cvv):
    #     response = self.client.service.FaSyndarkortnumer(
    #         Notandanafn=self.USERNAME,
    #         Lykilord=self.PASSWORD,
    #         Samningsnumer=self.CONTRACT_NUMBER,
    #         SamningsKennitala=self.CONTRACT_ID,
    #         PosiID=self.POSI_ID,
    #         Kortnumer=card_number,
    #         Gildistimi="{}{}".format(valid_until_month, valid_until_year),
    #         Oryggisnumer=cvv,
    #         Stillingar=''
    #     )

    #     self.check_error(response)

    #     return response['Syndarkortnumer']


    # def FaSidustuFjoraIKortnumeriUtFraSyndarkortnumeri(self, card_number_virtual):
    #     response = self.client.service.FaSidustuFjoraIKortnumeriUtFraSyndarkortnumeri(
    #         Notandanafn=self.USERNAME,
    #         Lykilord=self.PASSWORD,
    #         SamningsKennitala=self.CONTRACT_ID,
    #         Syndarkortnumer=card_number_virtual,
    #         Stillingar=''
    #     )
            
    #     self.check_error(response)

    #     return response['Kortnumer']


    # def FaHeimild(self, card_number_virtual, amount, currency='ISK'):
    #     response = self.client.service.FaHeimild(
    #         Notandanafn=self.USERNAME,
    #         Lykilord=self.PASSWORD,
    #         Samningsnumer=self.CONTRACT_NUMBER,
    #         SamningsKennitala=self.CONTRACT_ID,
    #         PosiID=self.POSI_ID,
    #         Syndarkortnumer=card_number_virtual,
    #         Upphaed=amount,
    #         Gjaldmidill=currency,
    #         Stillingar=''
    #     )
            
    #     self.check_error(response)

    #     return serialize_object(response['Kvittun'])


    # def FaEndurgreitt(self, card_number_virtual, amount, currency='ISK'):
    #     response = self.client.service.FaHeimild(
    #         Notandanafn=self.USERNAME,
    #         Lykilord=self.PASSWORD,
    #         Samningsnumer=self.CONTRACT_NUMBER,
    #         SamningsKennitala=self.CONTRACT_ID,
    #         PosiID=self.POSI_ID,
    #         Syndarkortnumer=card_number_virtual,
    #         Upphaed=amount,
    #         Gjaldmidill=currency,
    #         Stillingar=''
    #     )
            
    #     self.check_error(response)

    #     return serialize_object(response['Kvittun'])


    # def UppfaeraGildistima(self, card_number_virtual, valid_until_year, valid_until_month):
    #     response = self.client.service.UppfaeraGildistima(
    #         Notandanafn=self.USERNAME,
    #         Lykilord=self.PASSWORD,
    #         SamningsKennitala=self.CONTRACT_ID,
    #         Syndarkortnumer=card_number_virtual,
    #         NyrGildistimi="{}{}".format(valid_until_month, valid_until_year),
    #         Stillingar=''
    #     )
            
    #     self.check_error(response)

    #     return ""

