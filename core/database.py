"""
PostgreSQL Database Engine (SQLAlchemy Async)

Provides:
- Async engine and session factory for the application
- Sync engine for Alembic migrations
- Table creation utilities
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from config import POSTGRES_URL, POSTGRES_SYNC_URL


# ─── Declarative Base ───────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ─── Async Engine ───────────────────────────────────────────────
engine = create_async_engine(
    POSTGRES_URL,
    echo=False,          # Set True for SQL debug logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
)

# Session factory — produces AsyncSession instances
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """
    Dependency / context-manager helper.

    Usage:
        async with get_session() as session:
            ...
    Or as a generator for FastAPI-style DI.
    """
    async with async_session_factory() as session:
        yield session


async def init_db():
    """
    Create all tables defined via Base.metadata.

    Call once at application startup (before traffic).
    In production, prefer Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✓ PostgreSQL tables created / verified")


async def close_db():
    """Dispose of the connection pool on shutdown."""
    await engine.dispose()
    logger.info("✓ PostgreSQL connection pool closed")
