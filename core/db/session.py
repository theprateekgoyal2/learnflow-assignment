"""SQLAlchemy engine, session factory, and the get_db dependency."""

import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from core.config import config

# Enable FK enforcement on every SQLite connection
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    if isinstance(dbapi_conn, sqlite3.Connection):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


engine = create_engine(
    f"sqlite:///{config.DB_PATH}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a per-request Session, always closed after."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
