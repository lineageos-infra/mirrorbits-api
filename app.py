import redis

from flask import Flask, jsonify, request, Response
from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Gauge, Counter, Histogram
from time import time
#{b'sha256': b'fd5ef1c2aebb3228ed8c11136ecd973bc3564ead7d00638c52776d8ee4c5de39', b'md5': b'', b'sha1': b'81d5c7158cf1c7c7ced9481dc97c6b9b5a56fc29', b'modTime': b'2017-12-04 10:03:58.186652669 +0100 CET', b'size': b'362439627'}
#/full/bacon/20171127/lineage-14.1-20171127-nightly-bacon-signed.zip
r = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)

REQUEST_LATENCY = Histogram("flask_request_latency_seconds", "Request Latency", ['method', 'endpoint'])
REQUEST_COUNT = Counter("flask_request_count", "Request Count", ["method", "endpoint", "status"])

def get_builds(device=None):
    if device:
        path = "FILE_/full/{}/*".format(device)
    else:
        path = "FILE_/full/*"
    db = {}
    for key in r.keys(path):
        key = key.decode('utf-8')
        filepath = key[5:]
        _, _, device, date, filename = filepath.split('/')
        _, version, _, buildtype, _, _ = filename.split('-')
        h = r.hgetall(key)
        db.setdefault(device, []).append({
            'sha256': h[b'sha256'].decode('utf-8'),
            'sha1': h[b'sha1'].decode('utf-8'),
            'size': int(h[b'size'].decode('utf-8')),
            'date': '{}-{}-{}'.format(date[0:4], date[4:6], date[6:8]),
            'filename': filename,
            'filepath': filepath,
            'version': version,
            'type': buildtype
        })
    for key in db.keys():
        db[key] = sorted(db[key], key=lambda k: k['date'])
    return db

@app.before_request
def start_timer():
    request._stats_start = time()

@app.after_request
def stop_timer(response):
    delta = time() - request._stats_start
    REQUEST_LATENCY.labels(request.method, request.path).observe(delta)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

@app.route('/api/v1/builds/', defaults={'device': None})
@app.route('/api/v1/builds/<device>')
def get(device):
    return jsonify(get_builds(device))

@app.route('/api/metrics')
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
