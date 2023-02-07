FROM python:3.11.1-alpine

# set work directory
COPY . /usr/src/app/
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    libressl-dev libffi-dev gcc musl-dev python3-dev \
    bash \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/app/requirements.test.txt \
    && rm -rf /root/.cache/pip

EXPOSE 8000