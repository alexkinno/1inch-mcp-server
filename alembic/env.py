"""Alembic environment configuration for 1inch MCP Server."""

import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the models and configuration
from inch_mcp_server.database.models import Base
from inch_mcp_server.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from settings, converting async URL to sync for Alembic."""
    url = settings.database_url
    # Convert async URL to sync for Alembic
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg2")
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with a database connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from sqlalchemy.ext.asyncio import create_async_engine
    
    # Use the async URL for async engine
    async_url = settings.database_url
    
    connectable = create_async_engine(async_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Check if we're running with async database
    if settings.database_url.startswith("postgresql+asyncpg"):
        asyncio.run(run_async_migrations())
    else:
        # Sync database
        configuration = config.get_section(config.config_ini_section, {})
        configuration["sqlalchemy.url"] = get_url()
        
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 