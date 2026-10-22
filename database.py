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


# ==========================================
# DATABASE ENGINE
# ==========================================

engine_options: dict[str, Any] = {}

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
    Base class for all SQLAlchemy ORM models.

    Provides shared metadata and typed
    declarative model support.
    """

    pass


# ==========================================
# DATABASE DEPENDENCY
# ==========================================


def get_db() -> Generator[Session, None, None]:
    """
    Create a database session for a request.

    Yields:
        Session:
            A SQLAlchemy database session.

    The session is automatically closed after
    the request has finished.
    """

    db: Session = SessionLocal()

    try:
        yield db

    finally:
        db.close()
