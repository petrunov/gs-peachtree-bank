"""
Middleware functions for the Peachtree Bank API.
"""
from flask import request

def register_middleware(app):
    """Register middleware functions with the Flask app.
    
    Args:
        app: The Flask application instance.
    """
    @app.before_request
    def log_request():
        """Log the incoming request"""
        app.logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        """Log the response"""
        app.logger.info(f"Response: {response.status_code}")
        return response
