import unittest

from chatbot.config import Settings


class TestSettings(unittest.TestCase):
    def _create_settings(self, **kwargs) -> Settings:
        llms = kwargs.pop("llms", [{"api_key": "test_key"}])

        return Settings(llms=llms, **kwargs)

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
