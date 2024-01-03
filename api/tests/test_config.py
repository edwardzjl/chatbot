import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from chatbot.config import Settings


class TestSettings(unittest.TestCase):
    def test_default_inferece_url(self):
        settings = Settings()
        self.assertEqual(str(settings.inference_server_url), "http://localhost:8080/")

    @patch.dict(os.environ, {"INFERENCE_SERVER_URL": "http://foo.bar.com"}, clear=True)
    def test_inference_server_url(self):
        settings = Settings()
        self.assertEqual(str(settings.inference_server_url), "http://foo.bar.com/")

    def test_default_redis_om_url(self):
        settings = Settings()
        self.assertEqual(str(settings.redis_om_url), "redis://localhost:6379/0")

    @patch.dict(os.environ, {"REDIS_OM_URL": "redis://foo.bar.com:6379"}, clear=True)
    def test_redis_om_url(self):
        settings = Settings()
        self.assertEqual(str(settings.redis_om_url), "redis://foo.bar.com:6379/0")

    @patch.dict(
        os.environ, {"REDIS_OM_URL": "not-redis://foo.bar.com:6379"}, clear=True
    )
    def test_invalid_redis_om_url(self):
        with self.assertRaises(ValidationError):
            Settings()

    def test_default_user_id_header(self):
        settings = Settings()
        self.assertEqual(settings.user_id_header, "X-Forwarded-User")

    @patch.dict(os.environ, {"USER_ID_HEADER": "some-header"}, clear=True)
    def test_user_id_header(self):
        settings = Settings()
        self.assertEqual(settings.user_id_header, "some-header")


if __name__ == "__main__":
    unittest.main()
