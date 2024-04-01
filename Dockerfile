FROM python:3.6-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get -y install postgresql-client

WORKDIR /accuknox

COPY requirements.txt /accuknox/

RUN pip install --default-timeout=100 future --upgrade pip \
    && pip install -r requirements.txt \
    && pip list

COPY . /accuknox/

ENV PYTHONUNBUFFERED=1