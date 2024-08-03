import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from chatbot.config import Settings


class TestSettings(unittest.TestCase):
    def test_default_inferece_url(self):
        settings = Settings()
        self.assertEqual(str(settings.llm.url), "http://localhost:8080")

    @patch.dict(os.environ, {"LLM__URL": "http://foo.bar.com"}, clear=True)
    def test_inference_server_url(self):
        settings = Settings()
        self.assertEqual(str(settings.llm.url), "http://foo.bar.com/")

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


if __name__ == "__main__":
    unittest.main()
