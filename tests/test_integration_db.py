"""Integration checks that need a real Postgres/pgvector instance.

Skipped automatically when no database is reachable, so the default unit-test
run stays offline and fast. Run against a live DB with, e.g.::

    docker compose up -d db
    DB_URL=postgresql://myuser:mypassword@localhost:5433/mydb pytest tests/test_integration_db.py
"""
import os

import pytest

pytestmark = pytest.mark.integration


def _db_available() -> bool:
    try:
        from sqlalchemy import text

        from src.db.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


requires_db = pytest.mark.skipif(
    not os.environ.get("RUN_DB_TESTS") or not _db_available(),
    reason="No database available (set RUN_DB_TESTS=1 and a live DB_URL)",
)


@requires_db
def test_init_db_and_source_counts():
    from src.db.database import SessionLocal, init_db
    from src.db.models import Job

    init_db()
    with SessionLocal() as session:
        total = session.query(Job).count()
        assert total >= 0
