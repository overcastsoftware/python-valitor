Valitor python library
========================

Python implementation of the Valitor payments solution. Currently supported are:

    * Valitor Payments Gateway
    * ValitorPay


Test coverage
=============
<img width="628" alt="coverage" src="https://user-images.githubusercontent.com/143557/67790083-0a23ac00-fa6d-11e9-855e-1b646ec3c7a3.png">


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
```

`VALITOR_TEST_*` settings are used in the Valitor Payment Gateway. A new restful solution called Valitor Pay uses the `VALITORPAY_*` settings.