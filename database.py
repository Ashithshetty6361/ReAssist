"""
ReAssist Database Engine
Production-grade SQLAlchemy setup.
- Local dev: SQLite (zero install)
- Production: PostgreSQL (swap via DATABASE_URL env var)
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///reassist.db")

# SQLite needs check_same_thread=False for FastAPI's threaded model
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set True to debug SQL queries
    pool_pre_ping=True,  # Auto-reconnect stale connections (critical for Postgres)
)

# Enable WAL mode for SQLite (massive concurrent read perf improvement)
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency injection for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on startup."""
    from models import (  # noqa: F401 — must import to register models
        User, Workspace, Document, PipelineExecution, AgentTrace, ChatMessage
    )
    Base.metadata.create_all(bind=engine)
    print(f"[DB] Initialized database at: {DATABASE_URL}")
