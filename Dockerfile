FROM python:3.12-slim

COPY . /app

COPY requirements.txt ./app/requirements.txt
RUN pip install -r --no-cache ./app/requirements.txt

# TODO Доделать запуск