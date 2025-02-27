"""
Error handling module for the Flask API.
Defines custom exception classes and error handlers.
"""
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

    @app.errorhandler(500)
    def server_error(error):
        """Handler for 500 errors"""
        return jsonify({
            "error": "InternalServerError", 
            "message": "An unexpected error occurred"
        }), 500
