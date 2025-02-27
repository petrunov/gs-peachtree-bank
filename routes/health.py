"""
Health check endpoints for the Peachtree Bank API.
"""
from flask import Blueprint, jsonify
from flasgger import swag_from

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
# Rate limiting will be applied in app.py
@swag_from({
    "tags": ["Health"],
    "summary": "Health check endpoint",
    "description": "Returns the health status of the API",
    "responses": {
        "200": {
            "description": "API is healthy",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "healthy"
                    }
                }
            }
        }
    }
})
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({"status": "healthy"})
