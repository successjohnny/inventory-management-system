
import os
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./inventory.db",
)

# Use psycopg 3 for PostgreSQL connections.
# Neon provides URLs beginning with postgres://
# or postgresql://. SQLAlchemy needs the explicit
# postgresql+psycopg:// driver prefix.

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


# ==========================================
# DATABASE ENGINE
# ==========================================

engine_options: dict[str, Any] = {
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {
        "check_same_thread": False,
    }


engine: Engine = create_engine(
    DATABASE_URL,
    **engine_options,
)


# ==========================================
# DATABASE SESSION
# ==========================================

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==========================================
# DATABASE MODELS BASE
# ==========================================


class Base(DeclarativeBase):
    """
    Base for all SQLAlchemy ORM models.
    """

    pass


# ==========================================
# DATABASE DEPENDENCY
# ==========================================


def get_db() -> Generator[Session, None, None]:
    """
    Create a database session for a request.

    Automatically closes the session after
    the request has finished.
    """

    db: Session = SessionLocal()

    try:
        yield db

    finally:
        db.close()