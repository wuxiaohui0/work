# syntax=docker/dockerfile:1
###python3轻量级
FROM python:3.9-slim-buster

WORKDIR /test01

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]