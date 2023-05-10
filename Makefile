
.venv:
	python3 -mvenv .venv

.PHONY: .venv-activate
.venv-activate: .venv
	. .venv/bin/activate

.PHONY: deps
deps: pyproject.toml .venv-activate
	pip3 install poetry
	poetry install

poetry.lock: pyproject.toml .venv deps
	poetry update

.PHONY: .devcontainer/requirements.txt # Make does not automatically update when poetry.lock changes.
.devcontainer/requirements.txt: poetry.lock deps
	poetry export --without-hashes --format=requirements.txt --output=$@

.PHONY: docker-build
docker-build: .devcontainer/requirements.txt
	docker buildx build .

.PHONY: docker-build-no-cache
docker-build-no-cache: .devcontainer/requirements.txt
	docker buildx build --no-cache .
