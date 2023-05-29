FROM deepset/haystack:base-gpu-v1.17.0-rc2 AS build-image

ARG DEBIAN_FRONTEND=noninteractive

USER 0
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    vim \
    libfontconfig \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -d /app -u 1000 -g 0 -s /bin/bash cogniq

RUN chown cogniq /app

ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.in-project true && \
    poetry lock --no-interaction --no-ansi && \
    poetry install --no-interaction --no-ansi

COPY --from=deepset/xpdf:latest /opt/pdftotext /usr/local/bin

# The JSON schema is lazily generated at first usage, but we do it explicitly here for two reasons:
# - the schema will be already there when the container runs, saving the generation overhead when a container starts
# - derived images don't need to write the schema and can run with lower user privileges
RUN python3 -c "from haystack.utils.docker import cache_schema; cache_schema()"

# Haystack Preprocessor uses NLTK punkt model to divide text into a list of sentences.
# We cache these models for seemless user experience.
RUN python3 -c "from haystack.utils.docker import cache_nltk_model; cache_nltk_model()"

WORKDIR /app

COPY . ./


# Expose any ports the app is expected to run on
EXPOSE 3000
USER 1000

# If you have an entrypoint script, copy it and make it executable
# COPY docker-entrypoint.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# ENTRYPOINT ["docker-entrypoint.sh"]
