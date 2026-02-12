"""
Configuration settings for the Satellite Fire Detection System
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EmailConfig:
    """Email configuration for alerts"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = os.getenv("ALERT_EMAIL", "")
    sender_password: str = os.getenv("ALERT_EMAIL_PASSWORD", "")
    recipients: List[str] = None
    enabled: bool = False
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = [self.sender_email] if self.sender_email else []

@dataclass
class DatabaseConfig:
    """Database configuration for historical data"""
    db_path: str = "data/fire_history.db"
    max_history_days: int = 365
    backup_interval_hours: int = 24

@dataclass
class ExportConfig:
    """Export configuration"""
    export_dir: str = "exports"
    csv_delimiter: str = ","
    json_indent: int = 2

@dataclass
class MapConfig:
    """Map visualization configuration"""
    default_zoom: int = 8
    map_tile_provider: str = "OpenStreetMap"
    fire_marker_color: str = "red"
    smoke_marker_color: str = "orange"
    dust_marker_color: str = "brown"

class AppConfig:
    """Main application configuration"""
    
    # Model Configuration
    model_paths = {
        "smoke": "data/models/smoke_detection.onnx",
        "dust": "data/models/dust_detection.onnx"
    }
    confidence_threshold: float = 0.7
    max_image_size: int = 2048
    
    # API Configuration
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 60
    cache_timeout_minutes: int = 30
    
    # Email Configuration
    email = EmailConfig()
    
    # Database Configuration
    database = DatabaseConfig()
    
    # Export Configuration
    export = ExportConfig()
    
    # Map Configuration
    map = MapConfig()
    
    # NASA FIRMS API Configuration
    firms_api_base: str = "https://firms.modaps.eosdis.nasa.gov/api"
    firms_timeout_seconds: int = 30
    max_retries: int = 3
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    @classmethod
    def update_email_config(cls, config: Dict[str, Any]):
        """Update email configuration"""
        cls.email = EmailConfig(**config)
    
    @classmethod
    def update_database_config(cls, config: Dict[str, Any]):
        """Update database configuration"""
        cls.database = DatabaseConfig(**config)
    
    @classmethod
    def update_export_config(cls, config: Dict[str, Any]):
        """Update export configuration"""
        cls.export = ExportConfig(**config)
    
    @classmethod
    def update_map_config(cls, config: Dict[str, Any]):
        """Update map configuration"""
        cls.map = MapConfig(**config)

# Ensure directories exist
import os
os.makedirs("data", exist_ok=True)
os.makedirs("exports", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)