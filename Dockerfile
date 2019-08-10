# This Dockerfile uses multi-stage build to customize DEV and PROD images:
# https://docs.docker.com/develop/develop-images/multistage-build/
# 
# Based on: https://github.com/wemake-services/wemake-django-template/blob/master/%7B%7Bcookiecutter.project_name%7D%7D/docker/django/Dockerfile

FROM python:3.7.3-alpine3.9 as development_build

ARG ADVARCHS_ENV
ARG PIP_DISABLE_PIP_VERSION_CHECK=on

ENV ADVARCHS_ENV=${ADVARCHS_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=0.12.17


# System deps:
RUN apk --no-cache add \
     build-base \
     curl \
     gcc \
     git \
     libffi-dev \
     linux-headers \
     musl-dev \
     tini \
     p7zip \
  && pip install "poetry==$POETRY_VERSION"

# Copy only requirements, to cache them in docker layer
WORKDIR /pysetup
COPY ./poetry.lock ./pyproject.toml /pysetup/

# Project initialization:
RUN poetry config settings.virtualenvs.create false \
  && poetry install $(test "$ADVARCHS_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# This dir will become the mountpoint of development code
WORKDIR /code

FROM development_build as production_build

COPY . /code

ENTRYPOINT ["pytest"]