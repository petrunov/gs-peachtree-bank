"""
Index endpoint for the Peachtree Bank API.
"""
from flask import Blueprint, render_template

from extensions import limiter

# Create blueprint
index_bp = Blueprint('index', __name__, url_prefix='')

@index_bp.route('/', methods=['GET'])
@limiter.exempt  # No rate limit for documentation page
def index():
    """Root endpoint that displays available API endpoints."""
    return render_template('index.html')
