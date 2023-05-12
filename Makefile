APP:=CogniQ
LOWERCASE_APP:=$(shell echo $(APP) | tr '[:upper:]' '[:lower:]')
SHORT_SHA:=$(shell git rev-parse --short HEAD)
DIRTY:=$(shell git diff --quiet || echo "-dirty")
VERSION:=$(SHORT_SHA)$(DIRTY)
DOCKER_TAG:=$(LOWERCASE_APP):$(VERSION)

.venv:
	python3 -mvenv .venv

.PHONY: .venv-activate
.venv-activate: .venv
	. .venv/bin/activate

.PHONY: deps
deps: pyproject.toml .venv-activate
	pip3 install --upgrade poetry
	poetry update

poetry.lock: pyproject.toml .venv
	poetry update

.PHONY: docker-build
docker-build:
	docker buildx build -t $(DOCKER_TAG) .

.PHONY: docker-build-no-cache
docker-build-no-cache:
	docker buildx build -t $(DOCKER_TAG) --no-cache .
