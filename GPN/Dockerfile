FROM python:3.11.5

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .