format:
	black -l 79 *.py

.PHONY: format

test:
	pytest -v test.py

.PHONY: test
