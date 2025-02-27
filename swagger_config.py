"""
Swagger configuration for the Peachtree Bank API.
"""
from flasgger import Swagger

def configure_swagger(app):
    """Configure Swagger documentation for the Flask app.
    
    Args:
        app: The Flask application instance.
        
    Returns:
        The configured Swagger instance.
    """
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Peachtree Bank API",
            "description": "A simple REST API for Peachtree Bank",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@peachtreebank.com"
            }
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "tags": [
            {
                "name": "Health",
                "description": "Health check endpoints"
            },
            {
                "name": "Search",
                "description": "Search endpoints"
            },
            {
                "name": "Transactions",
                "description": "Transaction management endpoints"
            }
        ]
    }

    return Swagger(app, config=swagger_config, template=swagger_template)
