#
# Development support commands
#
SHELL := /bin/bash
SHELL_FLAGS := set -ue -o pipefail

FEDORA_PACKAGES = libpq-devel # needed for psycopg2
FEDORA_PACKAGES += postgres   # psql client
FEDORA_PACKAGES += pylint     # static code analysis tool

PYTHON_VENV_DIR = ./kafka

.PHONY: venv freeze pip-install dev-install syntax test static

default: syntax test

venv:
	python3 -m venv ${PYTHON_VENV_DIR}
	exec $(notdir $(SHELL))  -c 'source ${PYTHON_VENV_DIR}/bin/activate; bash -i'

freeze:
	pip freeze > requirements.txt

pip-install:
	pip install -r requirements.txt

dev-install:
	sudo dnf install ${FEDORA_PACKAGES}

# Check syntax of all Python sources but ignore PYTHON_VENV_DIR folder.

syntax:
	@${SHELL_FLAGS}; \
		for i in $$(find . -path ${PYTHON_VENV_DIR} -prune -false -o -name '*.py'); \
		do \
			echo -ne "$$i:\t"; \
			python -m py_compile $$i && echo "Syntax OK" ; \
			rm -f $${i}c; \
		done | column -t -s$$'\t'

# Unit tests

test:
	@${SHELL_FLAGS}; cd tests; \
		for i in test*.py; \
		do \
			echo -ne "Test case: $$i "; \
			python $$i >& /dev/null && echo "OK" || ( echo "ERROR"; exit 1 ); \
		done

# Static analysis

static:
	@${SHELL_FLAGS}; \
		${PYTHON_VENV_DIR}/bin/pylint src/*.py tests/*.py;

