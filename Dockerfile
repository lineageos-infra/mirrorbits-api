FROM python:3

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8084

CMD gunicorn -b 127.0.0.1:8084 -w 4 app:app
