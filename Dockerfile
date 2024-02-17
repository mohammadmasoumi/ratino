FROM python:3.10

RUN mkdir /divar_openplatform

WORKDIR /divar_openplatform

COPY requirements.txt /divar_openplatform/

RUN apt-get -y update \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . /divar_openplatform/

EXPOSE 8000

