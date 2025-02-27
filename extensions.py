"""
Flask extensions for the Peachtree Bank API.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from models import db

# Initialize rate limiter without app
limiter = Limiter(key_func=get_remote_address)

# Initialize database
migrate = None

def configure_extensions(app):
    """Configure Flask extensions for the application.
    
    Args:
        app: The Flask application instance.
    """
    # Configure rate limiting
    limiter.init_app(app)
    
    # Update limiter configuration from app config
    limiter.default_limits = app.config.get('RATELIMIT_DEFAULT_LIMITS', ["200 per day", "50 per hour"])
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URI', "memory://")
    limiter.strategy = app.config.get('RATELIMIT_STRATEGY', "fixed-window")
    
    # Initialize database
    db.init_app(app)
    global migrate
    migrate = Migrate(app, db)
