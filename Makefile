.PHONY: install test lint coverage shell

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m flake8 src/ tests/

coverage:
	$(PYTHON) -m pytest --cov=src/transcriptor_tracker tests/

shell: $(VENV)/bin/activate
	@echo "entering venv, type exit to quit"
	@PATH=$(shell pwd)/$(VENV)/bin:$$PATH bash