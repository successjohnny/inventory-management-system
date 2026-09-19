"""
Alembic migration environment.

Use the same database configuration as the FastAPI
application so migrations target the correct database.
"""

from logging.config import fileConfig

from alembic import context

from database import Base, DATABASE_URL, engine

# Import models so their tables are registered
# with Base.metadata for migration autogeneration.
from models import Product, StockMovement


# ==========================================
# ALEMBIC CONFIGURATION
# ==========================================

config = context.config


# ==========================================
# LOGGING CONFIGURATION
# ==========================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ==========================================
# MODEL METADATA
# ==========================================

target_metadata = Base.metadata


# ==========================================
# OFFLINE MIGRATIONS
# ==========================================

def run_migrations_offline() -> None:
    """
    Run migrations without opening a database connection.

    Use the application's configured database URL.
    """

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ==========================================
# ONLINE MIGRATIONS
# ==========================================

def run_migrations_online() -> None:
    """
    Run migrations using the application's database engine.
    """

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ==========================================
# EXECUTION MODE
# ==========================================

if context.is_offline_mode():
    run_migrations_offline()

else:
    run_migrations_online()