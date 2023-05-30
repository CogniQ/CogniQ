FROM deepset/haystack:base-gpu-v1.17.0-rc2 AS build-image

LABEL org.opencontainers.image.base.name="docker.io/deepset/haystack:base-gpu-v1.17.0-rc2" \
      org.opencontainers.image.description="Application packaged by CogniQ" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="CogniQ" \
      org.opencontainers.image.vendor="CogniQ" \
      org.opencontainers.image.source="https://github.com/CogniQ/CogniQ"

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

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry lock --no-interaction --no-ansi && \
    poetry install --no-interaction --no-ansi

WORKDIR /app

COPY . ./

# Expose any ports the app is expected to run on
EXPOSE 3000

USER 1000

ARG BUILD_TIME="2023-00-00T00:00:00Z"
ARG BUILD_VERSION="0.0.0+unversioned"
ARG BUILD_SHA="00000000"

LABEL org.opencontainers.image.created=${BUILD_TIME} \
      org.opencontainers.image.revision=${BUILD_SHA} \
      org.opencontainers.image.version=${BUILD_VERSION}