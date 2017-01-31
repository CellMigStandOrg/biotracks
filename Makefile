init:
	pip install -r requirements.txt

test:
	py.test -svx tests

.PHONY: init test
