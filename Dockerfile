FROM python:3

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8084

ENV prometheus_multiproc_dir=/app/metrics/

CMD gunicorn -b 0.0.0.0:8084 -w 4 app:app
