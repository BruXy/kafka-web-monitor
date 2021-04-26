#
# Development support commands
#

FEDORA_PACKAGES = libpq-devel # needed for psycopg2
FEDORA_PACKAGES += postgres   # psql client

PYTHON_VENV_DIR = ./kafka

.PHONY: venv freeze pip-install dev-install syntax test

default: syntax test

venv:
	python3 -m venv ${PYTHON_VENV_DIR}
	@echo "Activate:" source ${PYTHON_VENV_DIR}/bin/activate

freeze:
	pip freeze > requirements.txt

pip-install:
	pip install -r requirements.txt

dev-install:
	sudo dnf install ${FEDORA_PACKAGES}

# Check syntax of all Python sources but ignore PYTHON_VENV_DIR folder.

syntax:
	@set -ue -o pipefail; \
		for i in $$(find . -path ${PYTHON_VENV_DIR} -prune -false -o -name '*.py'); \
		do \
			echo -ne "$$i:\t"; \
			python -m py_compile $$i && echo "Syntax OK" ; \
			rm -f $${i}c; \
		done | column -t -s$$'\t'

# Unit tests

test:
	@set -ue -o pipefail; cd tests; \
		for i in test*.py; \
		do \
			echo -ne "Test case: $$i "; \
			python $$i >& /dev/null && echo "OK" || ( echo "ERROR"; exit 1 ); \
		done


