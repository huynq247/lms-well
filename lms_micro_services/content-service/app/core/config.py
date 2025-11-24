from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Content Service settings with flexible configuration"""
    
    # Environment info
    environment: str = "development"
    service_name: str = "content-service"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8002
    debug: bool = True
    allowed_hosts: List[str] = ["*"]
    
    # MongoDB configuration
    mongodb_url: str = os.environ.get("MONGODB_URL", "mongodb://admin:Mypassword123@14.161.50.86:27017/content_db?authSource=admin&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&socketTimeoutMS=10000")
    mongodb_db_name: str = os.environ.get("MONGODB_DB_NAME", "content_db")
    
    # Auth Service integration
    auth_service_url: str = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "microservices-lms-secret-key-2025-production-secure-auth-service")
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_expiration_time: int = 1440  # minutes
    
    # AI Configuration
    gemini_api_key: str = "your-gemini-api-key-here"
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"🔧 Content-service config loaded:")
        print(f"🔧 jwt_secret_key: {self.jwt_secret_key[:20]}...")
        print(f"🔧 jwt_algorithm: {self.jwt_algorithm}")
    
    # URL validation settings
    max_image_size_mb: int = 10
    max_video_size_mb: int = 100
    allowed_image_formats: str = "jpg,jpeg,png,gif,webp"
    allowed_video_formats: str = "mp4,avi,mov,wmv,flv,webm"
    
    @property
    def image_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.allowed_image_formats.split(",")]
    
    @property
    def video_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.allowed_video_formats.split(",")]
    
    # Redis cache (for future scaling)
    redis_url: Optional[str] = "redis://admin:Mypassword123@14.161.50.86:26379/1"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Request timeout settings
    request_timeout: int = 30
    url_validation_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Factory function for settings"""
    return Settings()

settings = get_settings()
