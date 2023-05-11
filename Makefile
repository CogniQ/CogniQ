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
	pip3 install poetry
	poetry install

poetry.lock: pyproject.toml .venv
	poetry update

.devcontainer/requirements.txt: poetry.lock
	poetry export --without-hashes --format=requirements.txt --output=$@

.PHONY: docker-build
docker-build: .devcontainer/requirements.txt
	docker buildx build -t $(DOCKER_TAG) .

.PHONY: docker-build-no-cache
docker-build-no-cache: .devcontainer/requirements.txt
	docker buildx build -t $(DOCKER_TAG) --no-cache .
