FROM python:3.9

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean -y

RUN pip install --upgrade pip
RUN pip install uwsgi 

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /backend

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

COPY . /backend

EXPOSE 5000