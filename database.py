import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./inventory.db",
)


# ==========================================
# DATABASE ENGINE
# ==========================================

engine_options = {}

if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {
        "check_same_thread": False,
    }


engine = create_engine(
    DATABASE_URL,
    **engine_options,
)


# ==========================================
# DATABASE SESSION
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==========================================
# DATABASE MODELS BASE
# ==========================================

Base = declarative_base()


# ==========================================
# DATABASE DEPENDENCY
# ==========================================

def get_db():
    """
    Create a database session for a request.

    The session is automatically closed after
    the request has finished.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()