"""
Application Configuration
Centralizes all settings — easy to change for dev/production.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration — used by all environments."""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # JSON settings
    JSON_SORT_KEYS = False
    
    # API
    API_PREFIX = "/api"
    
    # App info
    APP_NAME = "Smart Study Analyzer"
    APP_VERSION = "1.0.0"


class DevelopmentConfig(Config):
    """Development settings."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production settings."""
    DEBUG = False
    TESTING = False


# Choose config based on environment
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


def get_config():
    """Return the active configuration class."""
    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, DevelopmentConfig)
