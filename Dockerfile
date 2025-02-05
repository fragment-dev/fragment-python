FROM python:3.10.14-slim-bullseye

RUN apt-get update -y && apt-get install -y make

RUN pip install poetry

RUN mkdir -p /tmp/app
COPY . /tmp/app
WORKDIR /tmp/app

RUN poetry install --with dev
