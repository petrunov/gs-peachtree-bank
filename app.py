"""
Main application file for the Peachtree Bank API.
"""
import logging
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flasgger import Swagger, swag_from
from errors import register_error_handlers, ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from schemas import validate_request, TransactionSchema
from flask_migrate import Migrate
from models import db, Account, Transaction
from db import db_transaction, get_or_404
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Enable CORS for all API routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peachtree.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Swagger documentation
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
            "name": "Transactions",
            "description": "Transaction management endpoints"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

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


@app.route('/api/transactions', methods=['GET'])
@limiter.limit("30 per minute")
@swag_from({
    "tags": ["Transactions"],
    "summary": "Get all transactions",
    "description": "Returns a list of all transactions in the database",
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
})
def get_transactions():
    """Get all transactions.
    
    Returns a list of all transactions in the database.
    
    Query parameters:
    - limit: Maximum number of transactions to return (default: 100)
    - offset: Number of transactions to skip (default: 0)
    """
    # Get query parameters
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Limit the maximum number of transactions to return
    if limit > 100:
        limit = 100
    
    # Query transactions with pagination
    transactions = Transaction.query.order_by(Transaction.date.desc()).limit(limit).offset(offset).all()
    
    # Format the response
    result = []
    for transaction in transactions:
        result.append({
            "id": transaction.id,
            "date": transaction.date.isoformat(),
            "amount": str(transaction.amount),
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "beneficiary": transaction.beneficiary,
            "state": transaction.state,
            "description": transaction.description
        })
    
    # Return the transactions
    return jsonify(result)


@app.route('/api/transactions', methods=['POST'])
@limiter.limit("30 per minute")
@swag_from({
    "tags": ["Transactions"],
    "summary": "Create a new transaction",
    "description": "Creates a new transaction between accounts",
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
})
def create_transaction():
    """Create a new transaction.
    
    Accepts JSON with:
    - from_account_id: ID of the source account
    - to_account_id: ID of the destination account
    - amount: Amount to transfer
    - beneficiary: Name of the beneficiary
    - description: Optional description
    
    Returns the created transaction.
    """
    # Get JSON data from request
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")
    
    # Validate the request data
    validated_data = validate_request(TransactionSchema(), data)
    
    # Get the accounts
    from_account = get_or_404(Account, validated_data['from_account_id'])
    to_account = get_or_404(Account, validated_data['to_account_id'])
    
    # Check if accounts are different
    if from_account.id == to_account.id:
        raise ValidationError("Source and destination accounts must be different")
    
    # Check if source account has sufficient funds
    amount = Decimal(str(validated_data['amount']))
    if from_account.balance < amount:
        raise ValidationError("Insufficient funds in source account")
    
    # Create the transaction
    with db_transaction():
        # Create transaction record
        transaction = Transaction(
            date=validated_data.get('date'),
            amount=amount,
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            beneficiary=validated_data['beneficiary'],
            state='pending',
            description=validated_data.get('description', '')
        )
        db.session.add(transaction)
        
        # Update account balances
        from_account.balance -= amount
        to_account.balance += amount
        
        # Commit is handled by the context manager
    
    # Return the created transaction
    return jsonify({
        "id": transaction.id,
        "date": transaction.date.isoformat(),
        "amount": str(transaction.amount),
        "from_account_id": transaction.from_account_id,
        "to_account_id": transaction.to_account_id,
        "beneficiary": transaction.beneficiary,
        "state": transaction.state,
        "description": transaction.description
    }), 201


if __name__ == '__main__':
    app.run(debug=True)
