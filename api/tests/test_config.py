import unittest

from chatbot.config import Settings


class TestSettings(unittest.TestCase):
    def _create_settings(self, **kwargs) -> Settings:
        # NOTE: add base_url and "metadata" to avoid field validator guessing the provider
        llms = kwargs.pop(
            "llms",
            [
                {
                    "base_url": "foo.com",
                    "api_key": "test_key",
                    "metadata": {"provider": "vllm"},
                }
            ],
        )
        s3 = kwargs.pop("s3", {"bucket": "test_bucket"})

        return Settings(llms=llms, s3=s3, **kwargs)

    def test_db_primary_url_default(self):
        settings = self._create_settings()
        expected = "sqlite+aiosqlite:///chatbot.sqlite"
        self.assertEqual(str(settings.db_primary_url), expected)

    def test_db_primary_url_custom(self):
        custom_primary_url = (
            "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        )
        settings = self._create_settings(db_primary_url=custom_primary_url)
        expected = "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        self.assertEqual(str(settings.db_primary_url), expected)

    def test_db_standby_url_default(self):
        settings = self._create_settings()
        expected = "sqlite+aiosqlite:///chatbot.sqlite"
        self.assertEqual(str(settings.db_standby_url), expected)

    def test_db_standby_url_custom(self):
        custom_standby_url = (
            "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        )
        settings = self._create_settings(db_standby_url=custom_standby_url)
        expected = "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        self.assertEqual(str(settings.db_standby_url), expected)


if __name__ == "__main__":
    unittest.main()
