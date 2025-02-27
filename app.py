import logging
from flask import Flask, jsonify, render_template, request
from errors import register_error_handlers, ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate
from schemas import validate_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Register error handlers
register_error_handlers(app)

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Request/Response logging middleware
@app.before_request
def log_request():
    """Log the incoming request"""
    app.logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    """Log the response"""
    app.logger.info(f"Response: {response.status_code}")
    return response

@app.route('/', methods=['GET'])
@limiter.exempt  # No rate limit for documentation page
def index():
    """Root endpoint that displays available API endpoints."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
@limiter.limit("10 per minute")  # Custom rate limit for health endpoint
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({"status": "healthy"})


# Example schema for request validation
class MessageSchema(Schema):
    """Schema for validating message data."""
    message = fields.String(required=True, validate=validate.Length(min=1, max=100))
    priority = fields.Integer(validate=validate.Range(min=1, max=5))
    tags = fields.List(fields.String(), validate=validate.Length(max=5))

if __name__ == '__main__':
    app.run(debug=True)
