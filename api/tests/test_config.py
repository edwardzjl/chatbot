import unittest

from pydantic import ValidationError

from chatbot.config import Settings, remove_postgresql_variants


class TestRemovePostgresqlVariants(unittest.TestCase):
    def test_remove_psycopg(self):
        dsn = "postgresql+psycopg://user:pass@localhost/dbname"
        expected = "postgresql://user:pass@localhost/dbname"
        self.assertEqual(remove_postgresql_variants(dsn), expected)

    def test_remove_psycopg2(self):
        dsn = "postgresql+psycopg2://user:pass@localhost/dbname"
        expected = "postgresql://user:pass@localhost/dbname"
        self.assertEqual(remove_postgresql_variants(dsn), expected)

    def test_remove_psycopg2cffi(self):
        dsn = "postgresql+psycopg2cffi://user:pass@localhost/dbname"
        expected = "postgresql://user:pass@localhost/dbname"
        self.assertEqual(remove_postgresql_variants(dsn), expected)

    def test_no_change(self):
        dsn = "postgresql://user:pass@localhost/dbname"
        expected = "postgresql://user:pass@localhost/dbname"
        self.assertEqual(remove_postgresql_variants(dsn), expected)


class TestSettings(unittest.TestCase):
    def test_llm_default(self):
        settings = Settings()
        self.assertEqual(settings.llm, {"api_key": "NOT_SET"})

    def test_llm_custom(self):
        custom_llm = {"model": "gpt-3", "version": "davinci"}
        settings = Settings(llm=custom_llm)
        self.assertEqual(settings.llm, custom_llm)

    def test_psycopg_url_default(self):
        settings = Settings()
        expected = "postgresql://postgres:postgres@localhost:5432/"
        self.assertEqual(settings.psycopg_url, expected)

    def test_psycopg_url_custom(self):
        custom_url = "postgresql+psycopg2://custom_user:custom_pass@localhost/custom_db"
        settings = Settings(db_url=custom_url)
        expected = "postgresql://custom_user:custom_pass@localhost/custom_db"
        self.assertEqual(settings.psycopg_url, expected)

    def test_invalid_db_url(self):
        with self.assertRaises(ValidationError):
            Settings(db_url="invalid_url")


if __name__ == "__main__":
    unittest.main()
