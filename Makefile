DIRS := glitchtip_jira_bridge
POETRY_RUN := poetry run --no-ansi --no-interaction

format:
	$(POETRY_RUN) ruff check
	$(POETRY_RUN) ruff format
.PHONY: format

test:
	$(POETRY_RUN) ruff check --no-fix
	$(POETRY_RUN) ruff format --check
	$(POETRY_RUN) mypy
	$(POETRY_RUN) pytest -vv --cov=$(DIRS) --cov-report=term-missing --cov-report xml tests
.PHONY: test

pr-check:
	IMAGE_NAME=gjb-test NO_PUSH=1 TARGET=test-image ./build_deploy.sh
	docker run --rm gjb-test make test
.PHONY: pr-check
