FROM golang:1.17 as overmind
RUN GO111MODULE=on go get -u github.com/DarthSim/overmind/v2

FROM python:3.10
COPY --from=overmind /go/bin/overmind /usr/local/bin/overmind

RUN apt update && \
    apt install -y --no-install-recommends tmux

WORKDIR /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8084

ENV prometheus_multiproc_dir=/app/metrics/

CMD overmind start
