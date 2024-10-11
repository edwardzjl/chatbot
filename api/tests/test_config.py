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

    def test_postgres_primary_url_default(self):
        settings = Settings()
        expected = "postgresql+psycopg://postgres:postgres@localhost:5432/"
        self.assertEqual(str(settings.postgres_primary_url), expected)

    def test_postgres_primary_url_custom(self):
        custom_primary_url = (
            "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        )
        settings = Settings(postgres_primary_url=custom_primary_url)
        expected = "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        self.assertEqual(str(settings.postgres_primary_url), expected)

    def test_postgres_standby_url_default(self):
        settings = Settings()
        expected = "postgresql+psycopg://postgres:postgres@localhost:5432/"
        self.assertEqual(str(settings.postgres_standby_url), expected)

    def test_postgres_standby_url_custom(self):
        custom_standby_url = (
            "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        )
        settings = Settings(postgres_standby_url=custom_standby_url)
        expected = "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        self.assertEqual(str(settings.postgres_standby_url), expected)

    def test_invalid_db_url(self):
        with self.assertRaises(ValidationError):
            Settings(postgres_primary_url="invalid_url")
        with self.assertRaises(ValidationError):
            Settings(postgres_standby_url="invalid_url")

    def test_psycopg_primary_url_default(self):
        settings = Settings()
        expected = "postgresql://postgres:postgres@localhost:5432/"
        self.assertEqual(settings.psycopg_primary_url, expected)

    def test_psycopg_primary_url_custom(self):
        custom_primary_url = (
            "postgresql+psycopg://primary_user:primary_pass@localhost/primary_db"
        )
        settings = Settings(postgres_primary_url=custom_primary_url)
        expected = "postgresql://primary_user:primary_pass@localhost/primary_db"
        self.assertEqual(settings.psycopg_primary_url, expected)

    def test_psycopg_standby_url_default(self):
        settings = Settings()
        expected = "postgresql://postgres:postgres@localhost:5432/"
        self.assertEqual(settings.psycopg_standby_url, expected)

    def test_psycopg_standby_url_custom(self):
        custom_standby_url = (
            "postgresql+psycopg://standby_user:standby_pass@localhost/standby_db"
        )
        settings = Settings(postgres_standby_url=custom_standby_url)
        expected = "postgresql://standby_user:standby_pass@localhost/standby_db"
        self.assertEqual(settings.psycopg_standby_url, expected)


if __name__ == "__main__":
    unittest.main()
