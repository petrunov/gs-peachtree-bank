"""
Swagger configuration and API documentation for the Peachtree Bank API.
"""
from flasgger import Swagger, swag_from

# Swagger configuration
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

# Swagger template
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
            "name": "Transactions",
            "description": "Transaction management endpoints. The /api/transactions endpoint supports the following methods: GET (retrieve all transactions), POST (create a new transaction)"
        }
    ]
}

# Endpoint documentation
health_check_doc = {
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
}

get_transactions_doc = {
    "tags": ["Transactions"],
    "summary": "Get all transactions",
    "description": "Returns a list of all transactions in the database",
    "operationId": "getTransactions",
    "produces": ["application/json"],
    "methods": ["GET"],
    "parameters": [
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "description": "Maximum number of transactions to return",
            "default": 100,
            "required": False
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "description": "Number of transactions to skip",
            "default": 0,
            "required": False
        }
    ],
    "responses": {
        "200": {
            "description": "List of transactions",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "example": 1
                        },
                        "date": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-02-27T11:00:00.000Z"
                        },
                        "amount": {
                            "type": "string",
                            "example": "100.00"
                        },
                        "from_account_id": {
                            "type": "integer",
                            "example": 1
                        },
                        "to_account_id": {
                            "type": "integer",
                            "example": 2
                        },
                        "beneficiary": {
                            "type": "string",
                            "example": "John Doe"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["pending", "completed", "failed", "cancelled"],
                            "example": "pending"
                        },
                        "description": {
                            "type": "string",
                            "example": "Monthly rent payment"
                        }
                    }
                }
            }
        }
    }
}

create_transaction_doc = {
    "tags": ["Transactions"],
    "summary": "Create a new transaction",
    "description": "Creates a new transaction between accounts",
    "operationId": "createTransaction",
    "produces": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["from_account_id", "to_account_id", "amount", "beneficiary"],
                "properties": {
                    "from_account_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "to_account_id": {
                        "type": "integer",
                        "example": 2
                    },
                    "amount": {
                        "type": "string",
                        "example": "100.00"
                    },
                    "beneficiary": {
                        "type": "string",
                        "example": "John Doe"
                    },
                    "description": {
                        "type": "string",
                        "example": "Monthly rent payment"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Transaction created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2025-02-27T11:00:00.000Z"
                    },
                    "amount": {
                        "type": "string",
                        "example": "100.00"
                    },
                    "from_account_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "to_account_id": {
                        "type": "integer",
                        "example": 2
                    },
                    "beneficiary": {
                        "type": "string",
                        "example": "John Doe"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["pending", "completed", "failed", "cancelled"],
                        "example": "pending"
                    },
                    "description": {
                        "type": "string",
                        "example": "Monthly rent payment"
                    }
                }
            }
        },
        "400": {
            "description": "Validation error",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "ValidationError"
                    },
                    "message": {
                        "type": "string",
                        "example": "Request validation failed"
                    },
                    "details": {
                        "type": "object",
                        "example": {
                            "amount": ["Amount must be a positive number"]
                        }
                    }
                }
            }
        },
        "404": {
            "description": "Account not found",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "ResourceNotFoundError"
                    },
                    "message": {
                        "type": "string",
                        "example": "Account not found"
                    }
                }
            }
        }
    }
}

def init_swagger(app):
    """Initialize Swagger for the Flask application."""
    return Swagger(app, config=swagger_config, template=swagger_template)

def get_health_check_doc():
    """Get the Swagger documentation for the health check endpoint."""
    return health_check_doc

def get_transactions_doc():
    """Get the Swagger documentation for the get transactions endpoint."""
    return get_transactions_doc

def get_create_transaction_doc():
    """Get the Swagger documentation for the create transaction endpoint."""
    return create_transaction_doc
