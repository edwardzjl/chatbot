import os
import unittest
from unittest.mock import patch

from chatbot.config import Settings


class TestSettings(unittest.TestCase):
    def test_default_inferece_url(self):
        settings = Settings()
        self.assertEqual(str(settings.llm.url), "http://localhost:8080")

    @patch.dict(os.environ, {"LLM__URL": "http://foo.bar.com"}, clear=True)
    def test_inference_server_url(self):
        settings = Settings()
        self.assertEqual(str(settings.llm.url), "http://foo.bar.com/")


if __name__ == "__main__":
    unittest.main()
