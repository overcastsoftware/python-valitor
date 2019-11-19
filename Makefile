init:
	pip install -r requirements.txt

test:
	pytest -s -v --cov=valitor_python --cov-report=html tests

test_valitor:
	pytest -s -v -m valitor tests

test_currencies:
	pytest -s -v -m currencies tests

test_valitorpay:
	pytest -s -v -m valitorpay tests

test_valitorpaymentpage:
	pytest -s -v -m valitorpaymentpage tests
