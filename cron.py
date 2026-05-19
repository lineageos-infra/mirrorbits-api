import logging
import os
import sys
import redis
import json
from datetime import datetime
from time import mktime, time, sleep
from zipfile import ZipFile

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

BASE_PATH = os.environ.get("MIRROR_BASE_PATH", "/data/mirror")


def read_android_metadata(path, *keys):
    ret = [None] * len(keys)

    try:
        with ZipFile(path) as f:
            for line in f.read("META-INF/com/android/metadata").decode().splitlines():
                key, value = line.split("=", maxsplit=1)

                if key in keys:
                    ret[keys.index(key)] = value
    except:
        logging.warning(
            f"Failed to read META-INF/com/android/metadata for {path}", exc_info=True
        )

    return ret


def update_builds_v2():
    path = "FILE_/full/*.zip"
    db = {}
    for key in r.keys(path):
        key = key.decode("utf-8")
        filepath = key[5:]

        try:
            _, _, device, date, filename = filepath.split("/")
        except:
            logging.warning("Invalid filepath %s", filepath)
            continue

        try:
            _, version, _, buildtype, _, _ = filename.split("-")
        except:
            logging.warning("Invalid filename %s", filename)
            continue

        os_sdk_level, os_patch_level, timestamp = read_android_metadata(
            BASE_PATH + filepath,
            "post-sdk-level",
            "post-security-patch-level",
            "post-timestamp",
        )

        if not timestamp:
            timestamp = int(mktime(datetime.strptime(date, "%Y%m%d").timetuple()))
        else:
            timestamp = int(timestamp)

        info = {
            "date": "{}-{}-{}".format(date[0:4], date[4:6], date[6:8]),
            "datetime": timestamp,
            "version": version,
            "type": buildtype,
            "os_sdk_level": os_sdk_level,
            "os_patch_level": os_patch_level,
            "files": [],
        }

        artifacts_dir = os.path.dirname(key)
        for filekey in r.keys(artifacts_dir + "/*"):
            filekey = filekey.decode("utf-8")
            h = r.hgetall(filekey)
            filepath = filekey[5:]
            filename = os.path.basename(filepath)
            info["files"].append(
                {
                    "filepath": filepath,
                    "filename": filename,
                    "sha256": h[b"sha256"].decode("utf-8"),
                    "sha1": h[b"sha1"].decode("utf-8"),
                    "size": int(h[b"size"].decode("utf-8")),
                }
            )

        db.setdefault(device, []).append(info)
    for key in db.keys():
        db[key] = sorted(db[key], key=lambda k: k["datetime"])
    try:
        r.set("MIRRORBITS_API_V2_BUILDS", json.dumps(db))
    except:
        logging.warning("MIRRORBITS_API_V2_BUILDS update failed", exc_info=True)


if __name__ == "__main__":
    while True:
        logging.info("starting update")
        update_builds_v2()
        logging.info("update finished, sleeping 60m")
        sleep(3600)
