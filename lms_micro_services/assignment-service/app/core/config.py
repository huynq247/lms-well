from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = "development"
    service_name: str = "assignment-service"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8004
    debug: bool = True
    
    # Database
    database_url: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    # External Services
    auth_service_url: str = "http://localhost:8001"
    content_service_url: str = "http://localhost:8002"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    
    # Cache and Messaging
    redis_url: Optional[str] = None
    rabbitmq_url: Optional[str] = None
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Assignment Settings
    max_assignment_duration_days: int = 365
    progress_update_interval_minutes: int = 5
    session_timeout_minutes: int = 60
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
