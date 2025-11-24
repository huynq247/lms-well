from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Flexible database manager for single server and distributed setups"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.setup_connection()
    
    def setup_connection(self):
        """Setup database connection with flexible configuration"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                settings.database_url,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_timeout=settings.db_pool_timeout,
                pool_pre_ping=True,  # Verify connections before use
                echo=settings.debug  # SQL logging in debug mode
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database connection established for {settings.deployment_type}")
            logger.info(f"Environment: {settings.environment}")
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            self.setup_connection()
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connectivity test passed")
            return True
        except Exception as e:
            logger.error(f"Database connectivity test failed: {e}")
            return False

# Global database manager
db_manager = DatabaseManager()

# SQLAlchemy base
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

# Health check function
def check_database_health():
    """Check database health for monitoring"""
    return db_manager.test_connection()

# Export engine for external use (Alembic, scripts, etc.)
engine = db_manager.engine
