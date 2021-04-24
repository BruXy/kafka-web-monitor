.PHONY: venv freeze

venv:
	python3 -m venv ./kafka
	@echo "Activate:" source ./kafka/bin/activate

freeze:
	pip freeze > requirements.txt


