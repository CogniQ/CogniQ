FROM deepset/haystack:base-cpu-v1.20.0 AS build-image

LABEL org.opencontainers.image.base.name="docker.io/deepset/haystack:base-cpu-v1.20.0"q   \
      org.opencontainers.image.description="Application packaged by CogniQ" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="CogniQ" \
      org.opencontainers.image.vendor="CogniQ" \
      org.opencontainers.image.source="https://github.com/CogniQ/CogniQ" \
      org.opencontainers.image.url="https://cogniq.info"

ARG DEBIAN_FRONTEND=noninteractive

USER 0
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    vim \
    libfontconfig \
    git \
    gcc \
    postgresql-client \
    build-essential \
    python3-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -d /app -u 1000 -g 0 -s /bin/bash cogniq

RUN chown -R cogniq /app /tmp

# copy the Datadog `serverless-init` into your Docker image
COPY --from=datadog/serverless-init /datadog-init /app/datadog-init

ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --no-directory

WORKDIR /app

COPY . ./

# Expose any ports the app is expected to run on
EXPOSE 3000

USER 1000

# change the entrypoint to wrap your application into the Datadog serverless-init process
ENTRYPOINT ["/app/datadog-init"]

# execute your binary application wrapped in the entrypoint, launched by the Datadog trace library. Adapt this line to your needs
CMD ["ddtrace-run", "python", "main.py"]