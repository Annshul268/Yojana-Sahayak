"""Async Database Connection and Session Management."""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings
from backend.app.core.logging import logger

Base = declarative_base()


def get_database_url() -> str:
    """Returns the configured database URL with fallback to local SQLite."""
    url = settings.DATABASE_URL or os.getenv("DATABASE_URL")
    if not url:
        return "sqlite+aiosqlite:///./yojana_sahayak.db"
    # Ensure async driver for PostgreSQL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


DATABASE_URL = get_database_url()
is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initializes database tables and ensures new columns exist."""
    from sqlalchemy import text
    logger.info("Initializing database schema on %s...", "SQLite" if is_sqlite else "PostgreSQL")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Safe column additions for existing tables
        columns_to_add = [
            ("is_featured", "BOOLEAN DEFAULT 0"),
            ("featured_priority", "INTEGER DEFAULT 0"),
            ("image_url", "VARCHAR(500) DEFAULT NULL"),
        ]
        for col_name, typedef in columns_to_add:
            try:
                await conn.execute(text(f"ALTER TABLE schemes ADD COLUMN {col_name} {typedef}"))
            except Exception:
                pass  # column already exists
        try:
            await conn.execute(text("ALTER TABLE scheme_tracking ADD COLUMN applied_at DATETIME DEFAULT NULL"))
        except Exception:
            pass
        try:
            await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_scheme_tracking_user_scheme ON scheme_tracking(user_id, scheme_id)"))
        except Exception:
            pass
    logger.info("Database schema initialized successfully.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
