 # -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import base64
from .errors import ValitorPayException
import uuid
from enum import Enum
import requests
from .currencies import ISO4217 as Currency



class CardVerificationDataV2(object):
    def __init__(self, cavv, mdStatus=None, dsTransId=None):
        data = {
            'cavv': cavv,
        }
        if mdStatus:
            data['mdStatus'] = mdStatus
        if dsTransId:
            data['dsTransId'] = dsTransId
        self.data = data


class ValitorPayClient(object):

    def format_url(self, path):
        return "{}{}".format(self.ENDPOINT, path)

    def check_error(self, response):
        if response.status_code == 400:
            errors = response.json()
            output = ""
            for k, v in errors['errors'].items():
                vv = ", ".join("{}".format(x) for x in v)
                output += "{}: {}".format(k, vv)
            raise ValitorPayException(output)
        if response.status_code == 401:
            raise ValitorPayException("401 credentials error")


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
        Auth = 'Auth'
        Refund = 'Refund'
        Capture = 'Capture'
        CaptureRefund = 'CaptureRefund'
        RefundCancellation = 'RefundCancellation'


    class CardOperation(Enum):
        Sale = 'Sale'
        Refund = 'Refund'
        Auth = 'Auth'
        CardCheck = 'CardCheck'
        Capture = 'Capture'
        CaptureRefund = 'CaptureRefund'
        RefundCancellation = 'RefundCancellation'


    class CardHolderDeviceType(Enum):
        # Cardholder is connecting over the internet (web). This is the default, choose this option if you are unsure about what to choose.
        WWW = 'WWW' 
        MobileSdk = 'MobileSdk' # Mobile SDK (for ThreeDSecure 2.x only)
        ThreeRIFlow = 'ThreeRIFlow' #Mobile SDK (for ThreeDSecure 2.x only)


    class TransactionType(Enum):
        ECommerce = 'ECommerce'
        SubsequentTransaction = 'SubsequentTransaction'
        MailOrder = 'MailOrder'
        TelephoneOrder = 'TelephoneOrder'


    class ThreeDeeSecureResponseType(Enum):
        HTML = 'HTML' 
        JSON = 'JSON'


    def __init__(self, apikey, testing=True, apiversion='2.0'):
        self.APIKEY = apikey
        self.TESTING = testing
        self.APIVERSION = apiversion

        self.ENDPOINT = 'https://uat.valitorpay.com'
        if not testing:
            self.ENDPOINT = 'https://valitorpay.com'


    def make_request(self, action, method, **args):
        if method == 'POST':
            headers = {
                'Authorization': "APIKey {}".format(self.APIKEY),
                'valitorpay-api-version': self.APIVERSION,
            }
            response = requests.post(self.format_url(action), headers=headers, **args)

        self.check_error(response)
        return response.json()


    
    def CardVerification(self, cardNumber, expirationYear, expirationMonth, amount, currency, authenticationSuccessUrl, authenticationFailedUrl, merchantData='', subsequentTransactionType=SubsequentTransactionTypes.CardholderInitiatedCredentialOnFile, cardHolderDeviceType=CardHolderDeviceType.WWW, threeDeeSecureResponseType=ThreeDeeSecureResponseType.HTML):

        try:
            currency = Currency(currency)
        except ValueError:
            raise ValitorPayException(message="Invalid currency '{}'".format(currency))

        try:
            cardHolderDeviceType = ValitorPayClient.CardHolderDeviceType(cardHolderDeviceType)
        except ValueError:
            raise ValitorPayException(message="Invalid cardholder device type '{}'".format(cardHolderDeviceType))

        try:
            threeDeeSecureResponseType = ValitorPayClient.ThreeDeeSecureResponseType(threeDeeSecureResponseType)
        except ValueError:
            raise ValitorPayException(message="Invalid 3DS response type '{}'".format(threeDeeSecureResponseType))

        payload = {
            "amount": amount,
            "currency": currency.value,
            "cardNumber": cardNumber,
            "expirationMonth": expirationMonth,
            "expirationYear": expirationYear,
            "cardHolderDeviceType": cardHolderDeviceType.value,
            "merchantData": base64.b64encode(merchantData.encode()).decode('utf-8'),
            "authenticationSuccessUrl": authenticationSuccessUrl,
            "authenticationFailedUrl": authenticationFailedUrl,
        }

        response = self.make_request("/CardVerification", "POST", json=payload)
        if response["isSuccess"] == True:
            if threeDeeSecureResponseType == ValitorPayClient.ThreeDeeSecureResponseType.HTML:
                threedee_response = requests.post(response['postUrl'], data=dict(map(lambda x: (x['name'], x['value']), response['verificationFields'])))
                return threedee_response.text
            else:
                return {
                    'postUrl': response['postUrl'],
                    'verificationFields': dict(map(lambda x: (x['name'], x['value']), response['verificationFields'])),
                }
        else:
            raise ValitorPayException(message="Unsuccessful request")


    def CreateVirtualCard(self, cardNumber, expirationYear, expirationMonth, cvc, subsequentTransactionType=SubsequentTransactionTypes.CardholderInitiatedCredentialOnFile, cardVerificationData=None, currency=None):

        try:
            subsequentTransactionType = ValitorPayClient.SubsequentTransactionTypes(subsequentTransactionType)
        except ValueError:
            raise ValitorPayException(message="Invalid subsequent transaction type '{}'".format(subsequentTransactionType))

        if currency:
            try:
                currency = Currency(currency)
            except ValueError:
                raise ValitorPayException(message="Invalid currency '{}'".format(currency))


        payload = {
            "cardNumber": cardNumber,
            "expirationMonth": expirationMonth,
            "expirationYear": expirationYear,
            "cvc": cvc,
            "subsequentTransactionType": subsequentTransactionType.value,
        }        

        if currency:
            payload["currency"] = currency.value

        if cardVerificationData:
            cv_data = CardVerificationDataV2(**cardVerificationData)
            payload["cardVerificationData"] = cv_data.data
        
        return self.make_request("/VirtualCard/CreateVirtualCard", "POST", json=payload)


    def CardPayment(self, cardNumber, expirationYear, expirationMonth, cvc, amount, currency, operation, transactionType, acquirerReferenceNumber=None, cardVerificationData=None):
        
        try:
            currency = Currency(currency)
        except ValueError:
            raise ValitorPayException(message="Invalid currency '{}'".format(currency))

        try:
            operation = ValitorPayClient.CardOperation(operation)
        except ValueError:
            raise ValitorPayException(message="Invalid operation '{}'".format(operation))

        try:
            transactionType = ValitorPayClient.TransactionType(transactionType)
        except ValueError:
            raise ValitorPayException(message="Invalid transaction type '{}'".format(transactionType))

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
            assert operation == ValitorPayClient.CardOperation.Refund
            payload['acquirerReferenceNumber'] = acquirerReferenceNumber
    
            cv_data = CardVerificationDataV2(**cardVerificationData)
            payload["cardVerificationData"] = cv_data.data

        return self.make_request("/Payment/CardPayment", "POST", json=payload)



    def VirtualCardPayment(self, virtualCardNumber, amount, currency, operation, cardVerificationData=None, acquirerReferenceNumber=None):

        try:
            currency = Currency(currency)
        except ValueError:
            raise ValitorPayException(message="Invalid currency '{}'".format(currency))

        try:
            operation = ValitorPayClient.VirtualCardOperation(operation)
        except ValueError:
            raise ValitorPayException(message="Invalid operation '{}'".format(operation))

        
        if operation in [
            ValitorPayClient.VirtualCardOperation.Refund,
            ValitorPayClient.VirtualCardOperation.CaptureRefund,
            ValitorPayClient.VirtualCardOperation.Capture,
            ValitorPayClient.VirtualCardOperation.RefundCancellation
        ] and acquirerReferenceNumber == None:
            raise ValitorPayException(message="Acquirer reference number is required for this operation")


        payload = {
            'operation': operation.value,
            'currency': currency.value,
            'amount': amount,
            'virtualCardNumber': virtualCardNumber,
        } 

        if cardVerificationData:
            cv_data = CardVerificationDataV2(**cardVerificationData)
            payload["cardVerificationData"] = cv_data.data

        return self.make_request("/Payment/VirtualCardPayment", "POST", json=payload)


    def VirtualCardRefund(self, virtualCardNumber, amount, currency, acquirerReferenceNumber):

        try:
            currency = Currency(currency)
        except ValueError:
            raise ValitorPayException(message="Invalid currency '{}'".format(currency))

        operation = ValitorPayClient.VirtualCardOperation.Refund

        payload = {
            'operation': operation.value,
            'currency': currency.value,
            'amount': amount,
            'virtualCardNumber': virtualCardNumber,
            'acquirerReferenceNumber': acquirerReferenceNumber,
        } 

        return self.make_request("/Payment/VirtualCardPayment", "POST", json=payload)


    def UpdateExpirationDate(self, virtualCardNumber, expirationMonth, expirationYear):

        payload = {
            'expirationMonth': expirationMonth,
            'expirationYear': expirationYear,
            'virtualCardNumber': virtualCardNumber,
        } 

        return self.make_request("/VirtualCard/UpdateExpirationDate", "POST", json=payload)


    def GetVirtualCardData(self, virtualCardNumber):

        payload = {
            'virtualCard': virtualCardNumber,
        } 

        return self.make_request("/VirtualCard/GetVirtualCardData", "POST", json=payload)

