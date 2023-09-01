APP:=CogniQ
LOWERCASE_APP:=$(shell echo $(APP) | tr '[:upper:]' '[:lower:]')
SHORT_SHA:=$(shell git rev-parse --short HEAD)
DIRTY:=$(shell git diff --quiet || echo "-dirty")
VERSION:=$(SHORT_SHA)$(DIRTY)
DOCKER_TAG:=$(LOWERCASE_APP):$(VERSION)
TIMESTAMP:=$(shell date --iso-8601=seconds)


#: Display help
help:
	@ruby -e 'results = []; %w[$(MAKEFILE_LIST)].each {|file| File.read(file).scan(%r{(?<=^#: )(?<description>.+)\n(?:.PHONY: .*\n)*(?<target>^\S+):.*}) {results << $$~}}; padwidth=results.max_by{|e|e["target"].length}["target"].length; results.sort_by{|e|e["target"]}.each {|e|printf("%s: %s\n", e["target"].ljust(padwidth), e["description"].gsub("DANGER", "\u001b[31;1mDANGER\u001b[0m"))}'

.venv:
	python3 -mvenv .venv

.PHONY: .venv-activate
.venv-activate: .venv
	. .venv/bin/activate

.PHONY: deps
#: Installs the dependencies.
deps: pyproject.toml .venv-activate
	poetry lock
	poetry install --with localinstall

poetry.lock: pyproject.toml .venv
	poetry update

.PHONY: lint
#: Runs the linters.
lint:
	black .
	python -m mypy .

.PHONY: docker-build
#: Builds the Docker image.
docker-build:
	docker buildx build \
		-t $(DOCKER_TAG) \
		-t $(LOWERCASE_APP):local \
		--build-arg BUILD_TIME=$(TIMESTAMP) \
		--build-arg BUILD_VERSION=$(VERSION) \
		--build-arg BUILD_SHA=$(SHORT_SHA) \
		.

.PHONY: docker-build-no-cache
#: Builds the Docker image without using the cache.
docker-build-no-cache:
	docker build -t $(DOCKER_TAG) --no-cache .


.PHONY: docker-run
#: Starts the application locally in Docker Compose.
docker-run: .envrc docker-build
	docker-compose up

.PHONY: dc-up
#: Starts the application locally in Docker Compose. Alias for 'docker-run'.
dc-up: docker-run

.PHONY: update-containerapp
#: Updates the containerapp in Azure with the configuration in 'deployments/cogniq-community-main/containerapp.yml'.
update-containerapp:
	az containerapp update \
		--name cogniq \
		--resource-group cogniq-community-main \
		--yaml 'deployments/cogniq-community-main/containerapp.yml'


.PHONY: exec
#: Starts an SSH-like session on the main container.
# Useful for debugging. For example:
#  psql --username=${POSTGRES_USER} --host=${POSTGRES_HOST} --password cogniq
exec:
	az containerapp exec \
		--name cogniq \
		--resource-group cogniq-community-main \
		--command "/bin/bash"

.PHONY: logs
#: Follows the logs of the main container.
logs:
	az containerapp logs show \
		--name cogniq \
		--resource-group cogniq-community-main \
		--follow
