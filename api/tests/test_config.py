import unittest

from chatbot.config import Settings


class TestSettings(unittest.TestCase):
    def test_llm_default(self):
        settings = Settings()
        self.assertEqual(settings.llm, {"api_key": "NOT_SET"})

    def test_llm_custom(self):
        custom_llm = {"model": "gpt-3", "version": "davinci"}
        settings = Settings(llm=custom_llm)
        self.assertEqual(settings.llm, custom_llm)

    def test_db_primary_url_default(self):
        settings = Settings()
        expected = "sqlite+aiosqlite:///chatbot.sqlite"
        self.assertEqual(str(settings.db_primary_url), expected)

    def test_db_primary_url_custom(self):
        custom_primary_url = (
            "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        )
        settings = Settings(db_primary_url=custom_primary_url)
        expected = "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        self.assertEqual(str(settings.db_primary_url), expected)

    def test_db_standby_url_default(self):
        settings = Settings()
        expected = "sqlite+aiosqlite:///chatbot.sqlite"
        self.assertEqual(str(settings.db_standby_url), expected)

    def test_db_standby_url_custom(self):
        custom_standby_url = (
            "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        )
        settings = Settings(db_standby_url=custom_standby_url)
        expected = "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        self.assertEqual(str(settings.db_standby_url), expected)


if __name__ == "__main__":
    unittest.main()
