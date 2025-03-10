"""
Error handling module for the Flask API.
Defines custom exception classes and error handlers.
"""
import logging
from functools import wraps
from flask import jsonify


class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        self.message = message
        self.status_code = status_code
        self.payload = payload
        super().__init__(self.message)


class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found"""
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)


class ValidationError(APIError):
    """Raised when request validation fails"""
    def __init__(self, message="Validation error", payload=None):
        super().__init__(message, status_code=400, payload=payload)


class AuthorizationError(APIError):
    """Raised when authorization fails"""
    def __init__(self, message="Unauthorized", payload=None):
        super().__init__(message, status_code=401, payload=payload)


def handle_exceptions(app):
    """Decorator for standardizing exception handling in route functions.
    
    Usage:
        @app.route('/api/endpoint')
        @handle_exceptions(app)
        def my_route():
            # Route implementation
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except APIError:
                # Let our custom exceptions pass through to be handled by the registered handler
                raise
            except Exception as e:
                # Log the error
                app.logger.error(f"Unhandled exception in {f.__name__}: {str(e)}")
                # Convert to APIError
                raise APIError("An unexpected error occurred", status_code=500)
        return decorated_function
    return decorator


def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handler for our custom APIError exceptions"""
        response = {
            "error": error.__class__.__name__,
            "message": error.message
        }
        if error.payload:
            response["details"] = error.payload
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def not_found(error):
        """Handler for 404 errors"""
        return jsonify({
            "error": "NotFound", 
            "message": "The requested resource doesn't exist"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handler for 405 errors"""
        return jsonify({
            "error": "MethodNotAllowed", 
            "message": "The method is not allowed for the requested URL"
        }), 405

    @app.errorhandler(429)
    def ratelimit_error(error):
        """Handler for 429 Too Many Requests errors (rate limiting)"""
        return jsonify({
            "error": "RateLimitExceeded",
            "message": "Rate limit exceeded. Please try again later."
        }), 429

    @app.errorhandler(500)
    def server_error(error):
        """Handler for 500 errors"""
        return jsonify({
            "error": "InternalServerError", 
            "message": "An unexpected error occurred"
        }), 500
        
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handler for unexpected exceptions"""
        app.logger.error('Unexpected error: %s', str(error))
        return jsonify({
            "error": "UnexpectedError",
            "message": "An unexpected error occurred"
        }), 500
