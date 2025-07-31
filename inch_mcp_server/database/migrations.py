"""Database migration utilities for 1inch MCP Server."""

import asyncio
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from inch_mcp_server.config import settings
from inch_mcp_server.utils.logger_setup import setup_logger

logger = setup_logger("database.migrations")


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    # Get the project root directory (where alembic.ini should be)
    project_root = Path(__file__).parent.parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    
    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")
    
    config = Config(str(alembic_ini_path))
    
    # Override the sqlalchemy.url with our current database URL
    # Convert async URL to sync URL for Alembic
    sync_url = settings.database_url.replace("+asyncpg", "+psycopg2")
    config.set_main_option("sqlalchemy.url", sync_url)
    
    return config


def run_migrations_sync(target_revision: Optional[str] = "head") -> None:
    """Run database migrations synchronously."""
    try:
        config = get_alembic_config()
        logger.info(f"Running migrations to revision: {target_revision}")
        command.upgrade(config, target_revision)
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


async def run_migrations(target_revision: Optional[str] = "head") -> None:
    """Run database migrations asynchronously."""
    # Run migrations in a separate thread since Alembic is synchronous
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_migrations_sync, target_revision)


def get_current_revision() -> Optional[str]:
    """Get the current database revision."""
    try:
        # Create sync engine for checking revision
        sync_url = settings.database_url.replace("+asyncpg", "+psycopg2")
        engine = create_engine(sync_url)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    except Exception as e:
        logger.warning(f"Could not get current revision: {e}")
        return None


def check_migrations_needed() -> bool:
    """Check if migrations are needed."""
    try:
        config = get_alembic_config()
        script = ScriptDirectory.from_config(config)
        
        current_rev = get_current_revision()
        head_rev = script.get_current_head()
        
        logger.info(f"Current revision: {current_rev}, Head revision: {head_rev}")
        
        return current_rev != head_rev
    except Exception as e:
        logger.warning(f"Could not check migration status: {e}")
        return True  # Assume migrations are needed if we can't check


async def initialize_database() -> None:
    """Initialize database and run migrations if needed."""
    try:
        if settings.auto_migrate:
            logger.info("Auto-migration enabled, checking if migrations are needed...")
            
            if check_migrations_needed():
                logger.info("Running database migrations...")
                await run_migrations()
            else:
                logger.info("Database is up to date, no migrations needed")
        else:
            logger.info("Auto-migration disabled, skipping migration check")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
