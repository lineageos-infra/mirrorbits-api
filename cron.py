import logging
import os
import sys
import redis
import json
from datetime import datetime
from struct import unpack
from time import mktime, sleep

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


def read_os_patch_level(path):
    try:
        with open(path, "rb") as f:
            f.seek(8)  # ANDROID! (boot_magic)

            kernel_ramdisk_second_info = unpack("9I", f.read(9 * 4))
            header_version = kernel_ramdisk_second_info[8]

            # In header version 0, this field was used for DT size
            if header_version < 3 or header_version > 12:
                os_version_patch_level = unpack("I", f.read(1 * 4))[0]
            else:
                os_version_patch_level = kernel_ramdisk_second_info[2]

            os_patch_level = os_version_patch_level & ((1 << 11) - 1)

            if os_patch_level != 0:
                return "{:04d}-{:02d}".format(
                    2000 + (os_patch_level >> 4), os_patch_level & ((1 << 4) - 1)
                )
    except Exception:
        logging.warning(f"Failed to read SPL for {path}", exc_info=True)

    return None


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
            "os_patch_level": None,
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

            if filename == "boot.img":
                info["os_patch_level"] = read_os_patch_level(BASE_PATH + filepath)

        db.setdefault(device, []).append(info)
    for key in db.keys():
        db[key] = sorted(db[key], key=lambda k: k["datetime"])
    builds_v2 = db
    r.set("MIRRORBITS_API_V2_BUILDS", json.dumps(db))


if __name__ == "__main__":
    while True:
        logging.info("starting update")
        update_builds_v2()
        logging.info("update finished, sleeping 60m")
        sleep(3600)
