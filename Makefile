format:
	black -l 79 *.py
.PHONY: format

test:
	pytest -vv test.py
.PHONY: test
