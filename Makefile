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
	pip3 install --upgrade poetry
	poetry lock
	poetry install --with localinstall

poetry.lock: pyproject.toml .venv
	poetry update

.PHONY: docker-build
docker-build:
	docker buildx build \
		-t $(DOCKER_TAG) \
		--build-arg BUILD_TIME=$(TIMESTAMP) \
		--build-arg BUILD_VERSION=$(VERSION) \
		--build-arg BUILD_SHA=$(SHORT_SHA) \
		.

.PHONY: docker-build-no-cache
docker-build-no-cache:
	docker build -t $(DOCKER_TAG) --no-cache .


.PHONY: docker-run
docker-run: .envrc
	docker run \
		--env-file .env \
		$(DOCKER_TAG)

.PHONY: azure-container-logs
# It is presumed that the Azure CLI is installed and that the following environment variables are set:
# AZURE_RESOURCE_GROUP_NAME - the name of the Azure resource group
# It is further presumed that the name of the container is the same as the resource group name, though this is not necessarily the case.
azure-container-logs:
	az container attach \
		--resource-group $${AZURE_RESOURCE_GROUP_NAME:?} \
		--name $${AZURE_RESOURCE_GROUP_NAME:?}
