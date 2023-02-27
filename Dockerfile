FROM python:3.10

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8084

ENV prometheus_multiproc_dir=/app/metrics/

CMD gunicorn -b 127.0.0.1:8084 -w 8 -t 120 app:app
