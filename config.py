"""
Configuration settings for the Peachtree Bank API.
Defines different configurations for different environments.
"""
import os


class Config:
    """Base configuration class."""
    # Flask settings
    SECRET_KEY = 'dev-key-please-change-in-production'
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///peachtree.db'
    
    # Rate limiting settings
    RATELIMIT_DEFAULT_LIMITS = ["200 per day", "50 per hour"]
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    
    # Logging settings
    LOG_LEVEL = 'INFO'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)


# Dictionary mapping environment names to configuration classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    # Development is the default
    'default': DevelopmentConfig
}


def get_config():
    """Get the configuration based on the environment."""
    env = os.environ.get('FLASK_ENV', 'development')  # Development is default
    return config.get(env, config['default'])
