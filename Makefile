.PHONY: install test lint coverage shell docker-build docker-up docker-down docker-test

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

.env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Файл .env успешно создан из шаблона!"; \
		echo "ВНИМАНИЕ: Откройте файл .env и впишите ваш реальный GEMINI_API_KEY перед запуском."; \
	else \
		echo "Файл .env уже существует."; \
	fi

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

DOCKER_AUDIO ?= data/examples/sample-meeting.mp3
DOCKER_PROJECT_ID ?= edu
DOCKER_ISSUE_ID ?= 101

docker-build: .env
	docker compose build

docker-up: .env
	docker compose run --rm tracker $(DOCKER_AUDIO) --project-id "$(DOCKER_PROJECT_ID)" --issue-id "$(DOCKER_ISSUE_ID)"

docker-down:
	docker compose down -v

docker-test:
	docker compose run --rm -e PYTHONPATH=/app --entrypoint "pytest tests/" tracker

docker-lint:
	docker compose run --rm --entrypoint "flake8 src/ tests/" tracker

docker-coverage:
	docker compose run --rm -e PYTHONPATH=/app --entrypoint "pytest --cov=src/transcriptor_tracker tests/" tracker