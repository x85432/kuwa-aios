# syntax=docker/dockerfile:1
FROM python:3.10-slim AS build
# x86_64, aarch64
ARG ARCH=x86_64
# cpu, cu121
ARG IMAGE_VARIANT="cpu"

RUN apt-get update &&\
    apt-get install -y --no-install-recommends cmake build-essential git

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/kuwa

COPY docker/executor/requirements-${ARCH}-${IMAGE_VARIANT}.txt.lock ./requirements.txt.lock
COPY .git .git
COPY src/library src/library
COPY src/executor src/executor
COPY src/kernel src/kernel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip sync --force-reinstall --system \
    --link-mode copy --index-strategy unsafe-best-match requirements.txt.lock

# -----------------------------
FROM python:3.10-slim

# Install dependency for:
# llama-cpp-python: musl-dev
# ChromeDriver: libnss3-dev
# Whisper: ffmpeg
# Ref: https://github.com/abetlen/llama-cpp-python/issues/1628
RUN apt-get update && \
    apt-get install -y --no-install-recommends musl-dev libnss3-dev ffmpeg && \
    ln -s /usr/lib/$(uname -m)-linux-musl/libc.so /lib/libc.musl-$(uname -m).so.1 &&\
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/kuwa-executor

# Install source code of Kuwa Executors
COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build /usr/local/bin/kuwa-executor /usr/local/bin/kuwa-executor
COPY src/executor .

# Install the multi-chat-client and the entrypoint
COPY docker/executor/multi-chat-client/multi-chat-client /usr/local/bin/
COPY docker/executor/docker-entrypoint /usr/local/bin/
RUN chmod +x /usr/local/bin/multi-chat-client /usr/local/bin/docker-entrypoint

# Make the filesystem hierarchy of kuwa
ENV KUWA_ROOT="/var/kuwa/docker/root"
VOLUME ${KUWA_ROOT}
RUN mkdir -p ${KUWA_ROOT}/bin && \
    mkdir -p ${KUWA_ROOT}/database && \
    mkdir -p ${KUWA_ROOT}/custom
COPY src/tools ${KUWA_ROOT}/../../src/tools

# Default parameters
ENV no_proxy="kernel,web,localhost,127.0.0.0/8,::1,${no_proxy}"
ENV NO_PROXY="kernel,web,localhost,127.0.0.0/8,::1,${NO_PROXY}"
ENV EXECUTOR_TYPE="debug"
ENV EXECUTOR_ACCESS_CODE="debug"
ENV EXECUTOR_NAME="Debug Executor"
ENV EXECUTOR_IMAGE=""
ENV EXECUTOR_ORDER=""
ENV EXECUTOR_CREATE_BOT="true"
ENV ADD_EXECUTOR_TO_MULTI_CHAT="true"
ENV KERNEL_URL="http://kernel:9000/"
ENTRYPOINT [ "docker-entrypoint" ]
CMD []