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

    def test_api_call(self):
        response = self.app.get("/api/v2/builds/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
