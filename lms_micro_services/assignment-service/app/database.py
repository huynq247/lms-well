import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database URL - Use same database as auth service
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:Mypassword123@14.161.50.86:25432/postgres")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_recycle=300
)

# Create async session maker
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_database():
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """Initialize database tables"""
    try:
        # Test connection
        async with engine.begin() as conn:
            # Import models to register them
            from app.models.assignment import Assignment, Progress, StudySession
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


async def close_database():
    """Close database connections"""
    await engine.dispose()
