from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Main application settings with flexible configuration"""
    
    # Environment info
    environment: str = "development"
    deployment_type: str = "single-server"
    
    # Database configuration
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    
    # Shared services
    redis_url: str
    rabbitmq_url: str
    
    # Service discovery
    service_name: str = "auth-service"
    service_port: int = 8001
    local_ip: str
    public_ip: str
    
    # Future service communication
    content_service_url: Optional[str] = None
    assignment_service_url: Optional[str] = None
    api_gateway_url: Optional[str] = None
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Application settings
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    allowed_hosts: List[str] = ["*"]  # CORS allowed origins
    
    # Future scaling options (parsed from env)
    db_read_replicas: Optional[List[str]] = None
    redis_cluster_urls: Optional[List[str]] = None
    rabbitmq_cluster_urls: Optional[List[str]] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Factory function for settings"""
    return Settings()

settings = get_settings()
