"""
Main application file for the Peachtree Bank API.
"""
import logging
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from errors import register_error_handlers
from config import get_config
from routes.health import health_bp
from routes.search import search_bp
from routes.transactions import transactions_bp
from routes.index import index_bp
from middleware import register_middleware
from swagger_config import configure_swagger
from extensions import configure_extensions

# Load environment variables from .env file if it exists
load_dotenv()

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(health_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(index_bp)

def create_app(config_name=None):
    """Create and configure the Flask application.
    
    Args:
        config_name: The name of the configuration to use.
        
    Returns:
        The configured Flask application.
    """
    config = get_config(config_name)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = Flask(__name__)
    
    app.config.from_object(config)
    
    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
    
    swagger = configure_swagger(app)
    
    register_error_handlers(app)
    
    configure_extensions(app)
    
    register_blueprints(app)
    
    register_middleware(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
