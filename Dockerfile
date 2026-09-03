FROM python:3.14
RUN apt update && \
    apt install -y --no-install-recommends tmux

WORKDIR /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8084

ENV prometheus_multiproc_dir=/app/metrics/

CMD honcho start
