[![Build Status](https://travis-ci.org/overcastsoftware/python-valitor.svg?branch=master)](https://travis-ci.org/overcastsoftware/python-valitor)

Valitor python library
========================

Python implementation of the Valitor payments solution. Currently supported are:

 * Valitor Payments Gateway
 * ValitorPay
 * Valitor Hosted Payment Page


Test coverage
=============
<img width="694" alt="Coverage report" src="https://user-images.githubusercontent.com/143557/114572408-fa9b2180-9c66-11eb-9140-0f64da2ebd2f.png">


Testing
=======

You need to create a pytest.ini file in the project root with the following contents, you need to fill in the credentials supplied by Valitor:

```
[pytest]
env =
    VALITOR_TEST_USERNAME=<USERNAME>
    VALITOR_TEST_PASSWORD=<PASSWORD>
    VALITOR_TEST_CONTRACT_NUMBER=<CONTRACT_NUMBER>
    VALITOR_TEST_CONTRACT_ID=<CONTRACT_ID>
    VALITOR_TEST_POSI_ID=<POSI_ID>
    VALITOR_TEST_CARD=number:<test_number>,month:<test_month>,year:<test_year>,cvv:<test_cvv>,virtual:<expected_virtual_number>
    VALITORPAY_APIKEY=<APIKEY>
    VALITORPAY_TEST_CARD=number:<test_number>,month:<test_month>,year:<test_year>,cvv:<test_cvv>,virtual:<virtual_test_number>
    VALITOR_PAYMENTPAGE_MERCHANT_ID=<merchant_id>
    VALITOR_PAYMENTPAGE_VERIFICATION_CODE=<verification_code>
```

`VALITOR_TEST_*` settings are used in the Valitor Payment Gateway. A new restful solution called Valitor Pay uses the `VALITORPAY_*` settings.

The offsite payment page uses the `VALITOR_PAYMENTPAGE_*` settings.

Running tests
-------------

You can run the whole suite:

```
    make test
````

Or pick your module to test:

```
    make test_valitor
    make test_currencies
    make test_valitorpay
    make test_valitorpaymentpage
```


Valitor Payment Page
=====================

Basic usage
-----------

```
    from valitor_python import ValitorPaymentPageClient

    client = ValitorPaymentPageClient(merchant_id='YOUR ID', verification_code='YOUR SECRET', testing=False)
    client.set_option('Currency', 'ISK')

    client.add_product({
        'Quantity': 1,
        'Discount': 0,
        'Price': 1000,
        'Description': 'Product Description'
    })

    html = client.build_form_html()

```
