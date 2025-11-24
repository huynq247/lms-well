from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine for PostgreSQL
async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_database() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> bool:
    """Check database connectivity"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal
    
    async def connect_to_database(self):
        """Initialize database connection"""
        try:
            async with self.session_factory() as session:
                await session.execute(text("SELECT 1"))
            logger.info("✅ Connected to PostgreSQL database successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL database: {e}")
            raise
    
    async def disconnect_from_database(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("📴 Disconnected from PostgreSQL database")


# Global database manager instance
db_manager = DatabaseManager()
