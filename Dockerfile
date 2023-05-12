FROM bitnami/python:3.10.11 AS build-image

ARG DEBIAN_FRONTEND=noninteractive

USER 0
RUN install_packages \
    curl \
    vim \
    libfontconfig \
    git

RUN useradd -m -d /app -u 1001 -g 0 -s /bin/bash cogniq

RUN chown cogniq /app

ENV PATH="/app/.local/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY --from=deepset/xpdf:latest /opt/pdftotext /usr/local/bin


# RUN mkdir -p /opt/vendor
# COPY vendor/ /opt/vendor/

# Install NCCL https://developer.nvidia.com/nccl
# RUN cd /usr/local && tar -xvf /opt/vendor/nccl_2.18.1-1+cuda11.0_x86_64.txz

# Use a virtualenv we can copy over the next build stage
# RUN python3 -m venv --system-site-packages /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# The JSON schema is lazily generated at first usage, but we do it explicitly here for two reasons:
# - the schema will be already there when the container runs, saving the generation overhead when a container starts
# - derived images don't need to write the schema and can run with lower user privileges
RUN python3 -c "from haystack.utils.docker import cache_schema; cache_schema()"

# Haystack Preprocessor uses NLTK punkt model to divide text into a list of sentences.
# We cache these models for seemless user experience.
RUN python3 -c "from haystack.utils.docker import cache_nltk_model; cache_nltk_model()"

#ENV LD_LIBRARY_PATH="/opt/conda/lib"
#ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/conda/lib64"
#ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/conda/pkgs/pytorch-1.13.1-py3.10_cuda11.6_cudnn8.3.2_0/lib/python3.10/site-packages/torch/lib"
#ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/conda/nsight-compute/2022.4.0/host/target-linux-x64"
#ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/nccl_2.18.1-1+cuda11.0_x86_64/lib"

USER cogniq
WORKDIR /app

COPY . ./


# Expose any ports the app is expected to run on
EXPOSE 3000

# If you have an entrypoint script, copy it and make it executable
# COPY docker-entrypoint.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# ENTRYPOINT ["docker-entrypoint.sh"]
