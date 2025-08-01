"""Database connection management for 1inch MCP Server."""

from typing import AsyncGenerator, Union

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from inch_mcp_server.config import settings
from inch_mcp_server.utils.logger_setup import setup_logger

logger = setup_logger("database.connection")

# Global engine instance
_engine: Union[AsyncEngine, None] = None
_session_factory: Union[async_sessionmaker[AsyncSession], None] = None


def get_database_engine() -> AsyncEngine:
    """Get or create the database engine."""
    global _engine

    if _engine is None:
        # Configure engine for PostgreSQL
        _engine = create_async_engine(
            settings.database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )

        logger.info(
            f"Database engine created for: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}"
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory."""
    global _session_factory

    if _session_factory is None:
        engine = get_database_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
        logger.info("Database session factory created")

    return _session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database_connections():
    """Close all database connections."""
    global _engine, _session_factory

    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")
