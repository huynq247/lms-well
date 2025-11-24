import requests
import validators
from typing import Optional, Dict, Any
from PIL import Image
from io import BytesIO
import mimetypes
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class URLValidator:
    """URL validation utility for content service"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Content-Service-URL-Validator/1.0'
        })
    
    async def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate any URL and return detailed information"""
        if not url:
            return {
                "url": url,
                "is_valid": False,
                "error": "Empty URL"
            }
        
        # Basic URL format validation
        if not validators.url(url):
            return {
                "url": url,
                "is_valid": False,
                "error": "Invalid URL format"
            }
        
        try:
            # Make HEAD request first to get headers without downloading content
            response = self.session.head(
                url, 
                timeout=settings.url_validation_timeout,
                allow_redirects=True
            )
            
            # If HEAD fails, try GET with limited content
            if response.status_code >= 400:
                response = self.session.get(
                    url,
                    timeout=settings.url_validation_timeout,
                    allow_redirects=True,
                    stream=True
                )
            
            content_type = response.headers.get('content-type', '').lower()
            content_length = response.headers.get('content-length')
            
            result = {
                "url": url,
                "is_valid": response.status_code < 400,
                "status_code": response.status_code,
                "content_type": content_type,
                "content_length": int(content_length) if content_length else None
            }
            
            if response.status_code >= 400:
                result["error"] = f"HTTP {response.status_code}"
            
            return result
            
        except requests.RequestException as e:
            return {
                "url": url,
                "is_valid": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error validating URL {url}: {e}")
            return {
                "url": url,
                "is_valid": False,
                "error": "Validation failed"
            }
    
    async def validate_image_url(self, url: str) -> Dict[str, Any]:
        """Validate image URL specifically"""
        if not url:
            return {
                "url": url,
                "is_valid": False,
                "error": "Empty URL"
            }
        
        # Basic validation first
        basic_result = await self.validate_url(url)
        if not basic_result["is_valid"]:
            return basic_result
        
        try:
            # Check content type
            content_type = basic_result.get("content_type", "")
            if not content_type.startswith('image/'):
                return {
                    **basic_result,
                    "is_valid": False,
                    "error": f"Not an image (content-type: {content_type})"
                }
            
            # Check file extension
            file_extension = url.split('.')[-1].lower()
            if file_extension not in settings.image_formats_list:
                return {
                    **basic_result,
                    "is_valid": False,
                    "error": f"Unsupported image format: {file_extension}"
                }
            
            # Check file size
            content_length = basic_result.get("content_length")
            if content_length:
                max_size_bytes = settings.max_image_size_mb * 1024 * 1024
                if content_length > max_size_bytes:
                    return {
                        **basic_result,
                        "is_valid": False,
                        "error": f"Image too large: {content_length} bytes (max: {max_size_bytes})"
                    }
            
            # Try to load image to verify it's actually an image
            try:
                response = self.session.get(url, timeout=settings.url_validation_timeout, stream=True)
                response.raise_for_status()
                
                # Read only first chunk to verify image
                chunk = response.raw.read(8192)
                img = Image.open(BytesIO(chunk))
                
                basic_result.update({
                    "image_format": img.format,
                    "image_size": img.size if hasattr(img, 'size') else None
                })
                
            except Exception as img_error:
                return {
                    **basic_result,
                    "is_valid": False,
                    "error": f"Invalid image file: {str(img_error)}"
                }
            
            return basic_result
            
        except Exception as e:
            logger.error(f"Error validating image URL {url}: {e}")
            return {
                **basic_result,
                "is_valid": False,
                "error": "Image validation failed"
            }
    
    async def validate_video_url(self, url: str) -> Dict[str, Any]:
        """Validate video URL specifically"""
        if not url:
            return {
                "url": url,
                "is_valid": False,
                "error": "Empty URL"
            }
        
        # Check for common video platforms
        video_platforms = [
            'youtube.com', 'youtu.be',
            'vimeo.com',
            'dailymotion.com',
            'wistia.com',
            'jwplatform.com'
        ]
        
        # If it's a known platform, do basic validation
        for platform in video_platforms:
            if platform in url.lower():
                basic_result = await self.validate_url(url)
                if basic_result["is_valid"]:
                    basic_result["video_platform"] = platform
                return basic_result
        
        # For direct video URLs, do full validation
        basic_result = await self.validate_url(url)
        if not basic_result["is_valid"]:
            return basic_result
        
        try:
            # Check content type
            content_type = basic_result.get("content_type", "")
            if not (content_type.startswith('video/') or 'stream' in content_type):
                # Check file extension as fallback
                file_extension = url.split('.')[-1].lower()
                if file_extension not in settings.video_formats_list:
                    return {
                        **basic_result,
                        "is_valid": False,
                        "error": f"Not a video (content-type: {content_type}, extension: {file_extension})"
                    }
            
            # Check file size for direct video files
            content_length = basic_result.get("content_length")
            if content_length:
                max_size_bytes = settings.max_video_size_mb * 1024 * 1024
                if content_length > max_size_bytes:
                    return {
                        **basic_result,
                        "is_valid": False,
                        "error": f"Video too large: {content_length} bytes (max: {max_size_bytes})"
                    }
            
            return basic_result
            
        except Exception as e:
            logger.error(f"Error validating video URL {url}: {e}")
            return {
                **basic_result,
                "is_valid": False,
                "error": "Video validation failed"
            }
    
    def close(self):
        """Close the requests session"""
        self.session.close()

# Global URL validator instance
url_validator = URLValidator()
