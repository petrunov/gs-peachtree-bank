"""
Main application file for the Peachtree Bank API.
"""
import logging
from flask import Flask
from flask_cors import CORS
from errors import register_error_handlers
from config import get_config
from routes.health import health_bp
from routes.search import search_bp
from routes.transactions import transactions_bp
from routes.index import index_bp
from middleware import register_middleware
from swagger_config import configure_swagger
from extensions import configure_extensions

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
    # Get configuration based on environment
    config = get_config(config_name)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration from config object
    app.config.from_object(config)
    
    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Swagger documentation
    swagger = configure_swagger(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Configure extensions
    configure_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register middleware
    register_middleware(app)
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
