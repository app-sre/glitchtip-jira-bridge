DIRS := glitchtip_jira_bridge
POETRY_RUN := poetry run --no-ansi --no-interaction
IMAGE_NAME := glitchtip-jira-bridge

format:
	poetry run black $(DIRS)
	poetry run isort $(DIRS)
.PHONY: format

build-image:
	docker build -t $(IMAGE_NAME) .
.PHONY: build-image

pr-check: build-image
	docker run --rm $(IMAGE_NAME) make test
.PHONY: pr-check

test:
	poetry run pytest --cov=$(DIRS) --cov-report=term-missing --cov-fail-under=95 --cov-report xml tests
	poetry run flake8 $(DIRS)
	poetry run pylint --extension-pkg-whitelist='pydantic' $(DIRS)
	poetry run mypy $(DIRS)
	poetry run black --check $(DIRS)
	poetry run isort --check-only $(DIRS)
.PHONY: test

# build-deploy:
# 	docker build -t qontract-development-test  --progress plain --build-arg MAKE_TARGET=pypi .
# .PHONY: build-deploy
