DIRS := glitchtip_jira_bridge
POETRY_RUN := poetry run --no-ansi --no-interaction

format:
	$(POETRY_RUN) black $(DIRS)
	$(POETRY_RUN) isort $(DIRS)
.PHONY: format

test:
	$(POETRY_RUN) pytest --cov=$(DIRS) --cov-report=term-missing --cov-fail-under=95 --cov-report xml tests
	$(POETRY_RUN) flake8 $(DIRS)
	$(POETRY_RUN) pylint --extension-pkg-whitelist='pydantic' $(DIRS)
	$(POETRY_RUN) mypy $(DIRS)
	$(POETRY_RUN) black --check $(DIRS)
	$(POETRY_RUN) isort --check-only $(DIRS)
.PHONY: test

pr-check:
	IMAGE_NAME=gjb-test NO_PUSH=1 TARGET=test-image ./build_deploy.sh
	docker run --rm gjb-test make test
.PHONY: pr-check
