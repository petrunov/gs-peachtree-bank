"""
Configuration settings for the Peachtree Bank API.
Uses environment variables with sensible defaults for development.
"""
import os


class Config:
    """Configuration class using environment variables with defaults."""
    # Flask settings
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', 'yes', '1')
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///peachtree.db')
    
    # Rate limiting settings
    RATELIMIT_DEFAULT_LIMITS = os.environ.get('RATELIMIT_DEFAULT_LIMITS', "200 per day, 50 per hour").split(',')
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', "memory://")
    RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', "fixed-window")
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')


def get_config(config_name=None):
    """Get the configuration.
    
    Args:
        config_name: Not used, kept for backward compatibility.
    
    Returns:
        The configuration class.
    """
    return Config
