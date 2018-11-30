init:
	pip install -r requirements.txt

test:
	pytest -s -v tests
