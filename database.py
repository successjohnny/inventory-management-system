
import os
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeMeta,
    Session,
    declarative_base,
    sessionmaker,
)


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

# Data type: str
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./inventory.db",
)


# ==========================================
# DATABASE ENGINE
# ==========================================

# Data type: dict[str, Any]
engine_options: dict[str, Any] = {}

if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {
        "check_same_thread": False,
    }


# Data type: Engine
engine: Engine = create_engine(
    DATABASE_URL,
    **engine_options,
)


# ==========================================
# DATABASE SESSION
# ==========================================

# Data type: sessionmaker[Session]
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==========================================
# DATABASE MODELS BASE
# ==========================================

# Data type: DeclarativeMeta
Base: DeclarativeMeta = declarative_base()


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

    # Data type: Session
    db: Session = SessionLocal()

    try:
        yield db

    finally:
        db.close()