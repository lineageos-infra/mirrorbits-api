import unittest

import redis
import fakeredis

redis.StrictRedis = fakeredis.FakeStrictRedis

import app
import cron


class TestGetBuilds(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        app.app.config["DEBUG"] = False
        self.app = app.app.test_client()
        cron.update_builds_v2()

    def test_api_call(self):
        response = self.app.get("/api/v2/builds/")
        self.assertEqual(response.status_code, 200)

    def test_deprecated_api_call(self):
        response = self.app.get("/api/v1/builds/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"error": "this is deprecated, use /v2/"})


if __name__ == "__main__":
    unittest.main()
