"""
SQL Database Configuration
Uses SQLAlchemy (Async) with SQLite for the CTF Security Lab
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database connection URL (SQLite in-memory or file-based)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ctf_lab.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for SQL models
Base = declarative_base()

async def init_sql_db():
    """Initialize SQL database and create tables"""
    async with engine.begin() as conn:
        # Import models here to ensure they are registered with Base
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: SQL Database initialized (SQLite)")

async def get_db():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
