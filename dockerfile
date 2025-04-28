FROM python:3.8-slim-buster


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --upgrade pip

RUN pip3 install --timeout=120 --retries=20 --no-cache-dir -i https://pypi.org/simple -r requirements.txt

COPY ./core /app/
