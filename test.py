import unittest

import redis
import fakeredis
redis.StrictRedis = fakeredis.FakeStrictRedis

import app


class TestGetBuilds(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        app.app.config["DEBUG"] = False
        self.app = app.app.test_client()

    def test_empty(self):
        self.assertEqual(app.get_builds(), {})

    def test_get(self):
        app.r.hmset("FILE_/full/bacon/19700101/lineage-0.0-19700101-nightly-bacon-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700101/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700102/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700103/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700104/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700105/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700106/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700107/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700108/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700109/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700110/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700111/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700112/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700113/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700114/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})
        app.r.hmset("FILE_/full/mata/19700115/lineage-0.0-19700101-nightly-mata-signed.zip", {"sha256": "sha256", "sha1": "sha1", "size": "4"})

        builds = app.get_builds()

        self.assertIn("bacon", builds)
        self.assertIn("mata", builds)
        self.assertEqual(len(builds['mata']), 15)
        self.assertEqual(len(builds['bacon']), 1)

    def test_api_call(self):
        response = self.app.get("/api/v1/builds/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
