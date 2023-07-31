import logging
import os
import sys
import redis
import json
from datetime import datetime
from time import mktime, time, sleep

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


def update_builds_v2():
    path = "FILE_/full/*.zip"
    db = {}
    for key in r.keys(path):
        key = key.decode("utf-8")
        filepath = key[5:]
        _, _, device, date, filename = filepath.split("/")
        _, version, _, buildtype, _, _ = filename.split("-")

        timestamp = int(mktime(datetime.strptime(date, "%Y%m%d").timetuple()))

        info = {
            "date": "{}-{}-{}".format(date[0:4], date[4:6], date[6:8]),
            "datetime": timestamp,
            "version": version,
            "type": buildtype,
            "files": [],
        }

        artifacts_dir = os.path.dirname(key)
        for filekey in r.keys(artifacts_dir + "/*"):
            filekey = filekey.decode("utf-8")
            h = r.hgetall(filekey)
            filepath = filekey[5:]
            info["files"].append(
                {
                    "filepath": filepath,
                    "filename": os.path.basename(filepath),
                    "sha256": h[b"sha256"].decode("utf-8"),
                    "sha1": h[b"sha1"].decode("utf-8"),
                    "size": int(h[b"size"].decode("utf-8")),
                }
            )

        db.setdefault(device, []).append(info)
    for key in db.keys():
        db[key] = sorted(db[key], key=lambda k: k["datetime"])
    builds_v2 = db
    r.set("MIRRORBITS_API_V2_BUILDS", json.dumps(db))


if __name__ == "__main__":
    logging.info("starting update")
    update_builds_v2()
    logging.info("update finished, sleeping 60m")
    sleep(3600)
