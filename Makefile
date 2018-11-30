init:
	pip install -r requirements.txt

test:
	pytest -s -v --cov=valitor_python --cov-report=html tests
