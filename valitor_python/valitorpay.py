# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from .errors import ValitorPayException
import uuid
from enum import Enum
import requests
from .currencies import ISO4217 as Currency

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


    class VirtualCardOperation(Enum):
        Sale = 'Sale'
        Reversal = 'Reversal'


    class CardOperation(Enum):
        Sale = 'Sale'
        Reversal = 'Reversal'
        PreAuth = 'PreAuth'
        CardCheck = 'CardCheck'
        Advice = 'Advice'


    class TransactionType(Enum):
        ECommerce = 'ECommerce'
        SubsequentTransaction = 'SubsequentTransaction'
        MailOrder = 'MailOrder'
        TelephoneOrder = 'TelephoneOrder'


    def __init__(self, apikey, testing=True):
        self.APIKEY = apikey
        self.TESTING = testing

        if not testing:
            self.ENDPOINT = 'https://api.processing.valitor.com/Fyrirtaekjagreidslur/Fyrirtaekjagreidslur.asmx'


    def make_request(self, action, method, **args):
        if method == 'POST':
            response = requests.post(self.format_url(action), auth=(self.APIKEY, ''), **args)
        self.check_error(response)
        return response.json()


    def CreateVirtualCard(self, cardNumber, expirationYear, expirationMonth, cvc, subsequentTransactionType=SubsequentTransactionTypes.CardholderInitiatedCredentialOnFile, cardVerificationData=None):

        try:
            subsequentTransactionType = ValitorPayClient.SubsequentTransactionTypes(subsequentTransactionType)
        except ValueError:
            raise ValitorPayException(message=f"Invalid subsequent transaction type '{subsequentTransactionType}'")

        payload = {
            "cardNumber": cardNumber,
            "expirationMonth": expirationMonth,
            "expirationYear": expirationYear,
            "cvc": cvc,
            "subsequentTransactionType": subsequentTransactionType.value,
        }        

        if cardVerificationData:
            cv_data = CardVerificationData(**cardVerificationData)
            assert "cardholderAuthenticationVerificationData" in cardVerificationData
            payload["cardVerificationData"] = cardVerificationData

        return self.make_request("/VirtualCard/CreateVirtualCard", "POST", json=payload)


    def CardPayment(self, cardNumber, expirationYear, expirationMonth, cvc, operation, transactionType, currency, amount, acquirerReferenceNumber=None, cardVerificationData=None):
        
        try:
            currency = Currency(currency)
        except ValueError:
            raise ValitorPayException(message=f"Invalid currency '{currency}'")

        try:
            operation = ValitorPayClient.CardOperation(operation)
        except ValueError:
            raise ValitorPayException(message=f"Invalid operation '{operation}'")

        try:
            transactionType = ValitorPayClient.TransactionType(transactionType)
        except ValueError:
            raise ValitorPayException(message=f"Invalid transaction type '{transactionType}'")

        payload = {
            "cardNumber": cardNumber,
            "expirationMonth": expirationMonth,
            "expirationYear": expirationYear,
            "cvc": cvc,
            "transactionType": transactionType.value,
            'operation': operation.value,
            'currency': currency.value,
            'amount': amount,
        }  

        if acquirerReferenceNumber:
            assert operation == ValitorPayClient.CardOperation.Reversal
            payload['acquirerReferenceNumber'] = acquirerReferenceNumber
    
        if cardVerificationData:
            cv_data = CardVerificationData(**cardVerificationData)
            assert "cardholderAuthenticationVerificationData" in cardVerificationData
            payload["cardVerificationData"] = cardVerificationData

        return self.make_request("/Payment/CardPayment", "POST", json=payload)



    def VirtualCardPayment(self, virtualCardNumber, currency, amount, operation):

        try:
            currency = Currency(currency)
        except ValueError:
            raise ValitorPayException(message=f"Invalid currency '{currency}'")

        try:
            operation = ValitorPayClient.VirtualCardOperation(operation)
        except ValueError:
            raise ValitorPayException(message=f"Invalid operation '{operation}'")


        payload = {
            'operation': operation.value,
            'currency': currency.value,
            'amount': amount,
            'virtualCardNumber': virtualCardNumber,
        } 

        return self.make_request("/Payment/VirtualCardPayment", "POST", json=payload)


