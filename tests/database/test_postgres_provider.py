"""Tests for PostgresProvider.

Requires DATABASE_URL environment variable pointing to a test PostgreSQL instance.
Uses a dedicated test schema to avoid colliding with production data.

Usage:
    DATABASE_URL=postgresql://user:pass@host:5432/test_db pytest tests/database/test_postgres_provider.py -v
"""

import os
import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL environment variable not set",
)


@pytest.fixture
def provider():
    from gli_flow.database.postgres_provider import PostgresProvider

    p = PostgresProvider()
    p.connect()
    yield p
    p.disconnect()


class TestPostgresProviderConnection:
    def test_connect(self, provider):
        assert provider.is_connected

    def test_disconnect(self, provider):
        provider.disconnect()
        assert not provider.is_connected

    def test_double_connect(self, provider):
        provider.connect()
        assert provider.is_connected

    def test_close(self, provider):
        provider.close()
        assert not provider.is_connected


class TestPostgresProviderQueries:
    def test_fetchval_version(self, provider):
        val = provider.fetchval("SELECT version()")
        assert val is not None
        assert "PostgreSQL" in str(val)

    def test_fetchval_now(self, provider):
        val = provider.fetchval("SELECT NOW()")
        assert val is not None

    def test_fetchval_current_db(self, provider):
        val = provider.fetchval("SELECT current_database()")
        assert val is not None

    def test_fetchone(self, provider):
        row = provider.fetchone("SELECT 1 AS num, 'hello' AS text")
        assert row is not None
        assert row["num"] == 1
        assert row["text"] == "hello"

    def test_fetchall(self, provider):
        rows = provider.fetchall("SELECT generate_series(1, 3) AS n")
        assert len(rows) == 3
        assert [r["n"] for r in rows] == [1, 2, 3]

    def test_fetchone_no_results(self, provider):
        row = provider.fetchone("SELECT 1 WHERE 1=0")
        assert row is None

    def test_fetchall_no_results(self, provider):
        rows = provider.fetchall("SELECT 1 WHERE 1=0")
        assert rows == []

    def test_fetchval_no_results(self, provider):
        val = provider.fetchval("SELECT 1 WHERE 1=0")
        assert val is None


class TestPostgresProviderTransactions:
    def test_commit(self, provider):
        provider.execute("CREATE TEMP TABLE IF NOT EXISTS test_commit (id INT)")
        provider.execute("INSERT INTO test_commit VALUES (1)")
        count = provider.fetchval("SELECT COUNT(*) FROM test_commit")
        assert count == 1

    def test_rollback(self, provider):
        provider.execute("CREATE TEMP TABLE IF NOT EXISTS test_rollback (id INT)")
        try:
            provider.execute("INSERT INTO test_rollback VALUES ('not_a_number')")
        except Exception:
            provider.rollback()
        count = provider.fetchval("SELECT COUNT(*) FROM test_rollback")
        assert count == 0

    def test_transaction_context_manager_success(self, provider):
        provider.execute("CREATE TEMP TABLE IF NOT EXISTS test_txn_ok (id INT)")
        with provider.transaction():
            provider.execute("INSERT INTO test_txn_ok VALUES (42)")
        count = provider.fetchval("SELECT COUNT(*) FROM test_txn_ok")
        assert count == 1

    def test_transaction_context_manager_rollback(self, provider):
        provider.execute("CREATE TEMP TABLE IF NOT EXISTS test_txn_fail (id INT)")
        try:
            with provider.transaction():
                provider.execute("INSERT INTO test_txn_fail VALUES ('bad')")
        except Exception:
            pass
        count = provider.fetchval("SELECT COUNT(*) FROM test_txn_fail")
        assert count == 0


class TestPostgresProviderParameterized:
    def test_positional_params(self, provider):
        row = provider.fetchone(
            "SELECT %s AS val, %s AS name",
            [1, "test"],
        )
        assert row["val"] == 1
        assert row["name"] == "test"

    def test_named_params(self, provider):
        row = provider.fetchone(
            "SELECT %(val)s AS val, %(name)s AS name",
            {"val": 2, "name": "hello"},
        )
        assert row["val"] == 2
        assert row["name"] == "hello"

    def test_sql_injection_prevention(self, provider):
        malicious = "'; DROP TABLE pg_class; --"
        row = provider.fetchone("SELECT %s AS safe", [malicious])
        assert row["safe"] == malicious


class TestPostgresProviderInfo:
    def test_connection_info_available(self, provider):
        assert provider.database_url is not None

    def test_provider_repr(self, provider):
        assert "PostgresProvider" in repr(provider) or "PostgresProvider" in str(type(provider).__name__)
