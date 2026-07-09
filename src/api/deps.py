from collections.abc import Iterator

from sqlalchemy.orm import Session

from src.db.database import SessionLocal


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a DB session and closing it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
