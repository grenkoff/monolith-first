FROM python:3.14.10-slim-bookworm

ARG PLAYWRIGHT
ARG PYTEST

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_ROOT_USER_ACTION=ignore

RUN pip install "playwright==${PLAYWRIGHT}" "pytest==${PYTEST}" \
  && playwright install --with-deps chromium \
  && chmod -R a+rX /ms-playwright \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /tests
