APP:=CogniQ
LOWERCASE_APP:=$(shell echo $(APP) | tr '[:upper:]' '[:lower:]')
SHORT_SHA:=$(shell git rev-parse --short HEAD)
DIRTY:=$(shell git diff --quiet || echo "-dirty")
VERSION:=$(SHORT_SHA)$(DIRTY)
DOCKER_TAG:=$(LOWERCASE_APP):$(VERSION)
TIMESTAMP:=$(shell date --iso-8601=seconds)

.venv:
	python3 -mvenv .venv

.PHONY: .venv-activate
.venv-activate: .venv
	. .venv/bin/activate

.PHONY: deps
deps: pyproject.toml .venv-activate
	poetry lock
	poetry install --with localinstall

poetry.lock: pyproject.toml .venv
	poetry update

.PHONY: lint
lint:
	black .
	python -m mypy .

.PHONY: docker-build
docker-build:
	docker buildx build \
		-t $(DOCKER_TAG) \
		-t $(LOWERCASE_APP):local \
		--build-arg BUILD_TIME=$(TIMESTAMP) \
		--build-arg BUILD_VERSION=$(VERSION) \
		--build-arg BUILD_SHA=$(SHORT_SHA) \
		.

.PHONY: docker-build-no-cache
docker-build-no-cache:
	docker build -t $(DOCKER_TAG) --no-cache .


.PHONY: docker-run
docker-run: .envrc docker-build
	docker-compose up

.PHONY: dc-up
dc-up: docker-run

.PHONY: update-containerapp
update-containerapp:
	az containerapp update \
		--name cogniq \
		--resource-group cogniq-community-main \
		--yaml 'deployments/cogniq-community-main/containerapp.yml'

.PHONY: logs
# It is presumed that the Azure CLI is installed and that the following environment variables are set:
# AZURE_RESOURCE_GROUP_NAME - the name of the Azure resource group
# It is further presumed that the name of the container is the same as the resource group name, though this is not necessarily the case.
logs:
	az containerapp logs show \
		--name cogniq \
		--resource-group cogniq-community-main \
		--follow
