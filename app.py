import json
import logging
import os
import sys
import random
import re
import redis

from datetime import datetime
from flask import Flask, jsonify, request, Response

from prometheus_client import multiprocess
from prometheus_client import (
    generate_latest,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    Gauge,
    Counter,
    Histogram,
)
from time import mktime, time


root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

# {b'sha256': b'fd5ef1c2aebb3228ed8c11136ecd973bc3564ead7d00638c52776d8ee4c5de39', b'md5': b'', b'sha1': b'81d5c7158cf1c7c7ced9481dc97c6b9b5a56fc29', b'modTime': b'2017-12-04 10:03:58.186652669 +0100 CET', b'size': b'362439627'}
# /full/bacon/20171127/lineage-14.1-20171127-nightly-bacon-signed.zip
r = redis.StrictRedis(host="localhost", port=6379, db=0)

app = Flask(__name__)

REQUEST_LATENCY = Histogram(
    "flask_request_latency_seconds", "Request Latency", ["method", "endpoint"]
)
REQUEST_COUNT = Counter(
    "flask_request_count", "Request Count", ["method", "endpoint", "status"]
)
BASE_PATH = os.environ.get("MIRROR_BASE_PATH", "/data/mirror")

@app.before_request
def start_timer():
    request._stats_start = time()


@app.after_request
def stop_timer(response):
    delta = time() - request._stats_start
    REQUEST_LATENCY.labels(request.method, request.path).observe(delta)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response


@app.route("/api/v1/builds/", defaults={"device": None})
@app.route("/api/v1/builds/<device>")
def get_v1(device):
    return jsonify({"error": "this is deprecated, use /v2/"})


@app.route("/api/v2/builds/", defaults={"device": None})
@app.route("/api/v2/builds/<device>")
def get_v2(device):
    cache = r.get("MIRRORBITS_API_V2_BUILDS").decode("utf-8")
    builds_v2 = json.loads(cache)
    if device:
        return jsonify({device: builds_v2.get(device, [])})
    else:
        return jsonify(builds_v2)


@app.route("/api/metrics")
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
