"""
Main application file for the Peachtree Bank API.
"""
import logging
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flasgger import Swagger, swag_from
from errors import register_error_handlers, ValidationError, ResourceNotFoundError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from schemas import validate_request, TransactionSchema, TransactionQuerySchema, TransactionUpdateSchema
from flask_migrate import Migrate
from models import db, Account, Transaction, TransactionState
from db import db_transaction, get_or_404
from decimal import Decimal
from config import get_config
from sqlalchemy import or_, desc, asc

# Get configuration based on environment
config = get_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Load configuration from config object
app.config.from_object(config)

# Enable CORS for all API routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
            "name": "Search",
            "description": "Search endpoints"
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
    default_limits=config.RATELIMIT_DEFAULT_LIMITS,
    storage_uri=config.RATELIMIT_STORAGE_URI,
    strategy=config.RATELIMIT_STRATEGY
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

@app.route('/api/search', methods=['GET'])
@limiter.limit("30 per minute")
@swag_from({
    "tags": ["Search"],
    "summary": "Search accounts and transactions",
    "description": "Search for accounts and transactions by query string",
    "parameters": [
        {
            "name": "q",
            "in": "query",
            "type": "string",
            "description": "Search query",
            "required": True
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "description": "Maximum number of results to return",
            "default": 100,
            "required": False
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "description": "Number of results to skip",
            "default": 0,
            "required": False
        }
    ],
    "responses": {
        "200": {
            "description": "Search results",
            "schema": {
                "type": "object",
                "properties": {
                    "accounts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "example": 1
                                },
                                "account_number": {
                                    "type": "string",
                                    "example": "1234567890"
                                },
                                "account_name": {
                                    "type": "string",
                                    "example": "John Doe Checking"
                                },
                                "type": {
                                    "type": "string",
                                    "example": "account"
                                }
                            }
                        }
                    },
                    "transactions": {
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
                                "beneficiary": {
                                    "type": "string",
                                    "example": "John Doe"
                                },
                                "description": {
                                    "type": "string",
                                    "example": "Monthly rent payment"
                                },
                                "type": {
                                    "type": "string",
                                    "example": "transaction"
                                }
                            }
                        }
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
                        "example": "Search query is required"
                    }
                }
            }
        }
    }
})
def search():
    """Search for accounts and transactions.
    
    Returns accounts and transactions that match the search query.
    
    Query parameters:
    - q: Search query (required)
    - limit: Maximum number of results to return (default: 100)
    - offset: Number of results to skip (default: 0)
    """
    # Get query parameters
    query = request.args.get('q')
    if not query:
        raise ValidationError("Search query is required")
    
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Limit the maximum number of results to return
    if limit > 100:
        limit = 100
    
    # Search for accounts
    search_term = f"%{query}%"
    accounts = Account.query.filter(
        or_(
            Account.account_number.ilike(search_term),
            Account.account_name.ilike(search_term)
        )
    ).limit(limit).offset(offset).all()
    
    # Search for transactions
    transactions = Transaction.query.filter(
        or_(
            Transaction.beneficiary.ilike(search_term),
            Transaction.description.ilike(search_term)
        )
    ).limit(limit).offset(offset).all()
    
    # Format the response
    account_results = []
    for account in accounts:
        account_results.append({
            "id": account.id,
            "account_number": account.account_number,
            "account_name": account.account_name,
            "type": "account"
        })
    
    transaction_results = []
    for transaction in transactions:
        transaction_results.append({
            "id": transaction.id,
            "date": transaction.date.isoformat(),
            "amount": str(transaction.amount),
            "beneficiary": transaction.beneficiary,
            "description": transaction.description,
            "type": "transaction"
        })
    
    # Return the search results
    return jsonify({
        "accounts": account_results,
        "transactions": transaction_results
    })

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
        },
        {
            "name": "sort_by",
            "in": "query",
            "type": "string",
            "description": "Field to sort by",
            "enum": ["date", "amount", "beneficiary"],
            "default": "date",
            "required": False
        },
        {
            "name": "sort_order",
            "in": "query",
            "type": "string",
            "description": "Sort order",
            "enum": ["asc", "desc"],
            "default": "desc",
            "required": False
        },
        {
            "name": "search",
            "in": "query",
            "type": "string",
            "description": "Search query",
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
                            "enum": [state.value for state in TransactionState],
                            "example": TransactionState.SENT.value
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
    - sort_by: Field to sort by (date, amount, beneficiary) (default: date)
    - sort_order: Sort order (asc, desc) (default: desc)
    - search: Search query
    """
    # Validate query parameters
    query_params = {}
    for param in ['limit', 'offset', 'sort_by', 'sort_order', 'search']:
        if request.args.get(param):
            query_params[param] = request.args.get(param)
    
    # Validate and get parameters
    validated_params = validate_request(TransactionQuerySchema(), query_params)
    limit = validated_params.get('limit', 100)
    offset = validated_params.get('offset', 0)
    sort_by = validated_params.get('sort_by', 'date')
    sort_order = validated_params.get('sort_order', 'desc')
    search = validated_params.get('search')
    
    # Start building the query
    query = Transaction.query
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.beneficiary.ilike(search_term),
                Transaction.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == 'date':
        sort_column = Transaction.date
    elif sort_by == 'amount':
        sort_column = Transaction.amount
    elif sort_by == 'beneficiary':
        sort_column = Transaction.beneficiary
    else:
        sort_column = Transaction.date
    
    if sort_order == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Apply pagination
    transactions = query.limit(limit).offset(offset).all()
    
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

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@limiter.limit("30 per minute")
@swag_from({
    "tags": ["Transactions"],
    "summary": "Get transaction details",
    "description": "Returns details for a specific transaction",
    "parameters": [
        {
            "name": "transaction_id",
            "in": "path",
            "type": "integer",
            "description": "ID of the transaction to retrieve",
            "required": True
        }
    ],
    "responses": {
        "200": {
            "description": "Transaction details",
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
                        "enum": [state.value for state in TransactionState],
                        "example": TransactionState.SENT.value
                    },
                    "description": {
                        "type": "string",
                        "example": "Monthly rent payment"
                    }
                }
            }
        },
        "404": {
            "description": "Transaction not found",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "ResourceNotFoundError"
                    },
                    "message": {
                        "type": "string",
                        "example": "Transaction not found"
                    }
                }
            }
        }
    }
})
def get_transaction(transaction_id):
    """Get a specific transaction by ID.
    
    Returns details for a specific transaction.
    
    Path parameters:
    - transaction_id: ID of the transaction to retrieve
    """
    # Get the transaction
    transaction = get_or_404(Transaction, transaction_id)
    
    # Return the transaction details
    return jsonify({
        "id": transaction.id,
        "date": transaction.date.isoformat(),
        "amount": str(transaction.amount),
        "from_account_id": transaction.from_account_id,
        "to_account_id": transaction.to_account_id,
        "beneficiary": transaction.beneficiary,
        "state": transaction.state,
        "description": transaction.description
    })

@app.route('/api/transactions/<int:transaction_id>', methods=['PATCH'])
@limiter.limit("30 per minute")
@swag_from({
    "tags": ["Transactions"],
    "summary": "Update transaction state",
    "description": "Updates the state of a specific transaction",
    "parameters": [
        {
            "name": "transaction_id",
            "in": "path",
            "type": "integer",
            "description": "ID of the transaction to update",
            "required": True
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["state"],
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": [state.value for state in TransactionState],
                        "example": TransactionState.PAID.value
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Transaction updated successfully",
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
                        "enum": [state.value for state in TransactionState],
                        "example": TransactionState.PAID.value
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
                            "state": ["State must be one of: sent, received, paid"]
                        }
                    }
                }
            }
        },
        "404": {
            "description": "Transaction not found",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "ResourceNotFoundError"
                    },
                    "message": {
                        "type": "string",
                        "example": "Transaction not found"
                    }
                }
            }
        }
    }
})
def update_transaction(transaction_id):
    """Update a transaction's state.
    
    Updates the state of a specific transaction.
    
    Path parameters:
    - transaction_id: ID of the transaction to update
    
    Request body:
    - state: New state for the transaction (sent, received, paid)
    """
    # Get JSON data from request
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")
    
    # Validate the request data
    validated_data = validate_request(TransactionUpdateSchema(), data)
    
    # Get the transaction
    transaction = get_or_404(Transaction, transaction_id)
    
    # Update the transaction state
    with db_transaction():
        transaction.state = validated_data['state']
        # Commit is handled by the context manager
    
    # Return the updated transaction
    return jsonify({
        "id": transaction.id,
        "date": transaction.date.isoformat(),
        "amount": str(transaction.amount),
        "from_account_id": transaction.from_account_id,
        "to_account_id": transaction.to_account_id,
        "beneficiary": transaction.beneficiary,
        "state": transaction.state,
        "description": transaction.description
    })

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
                        "enum": [state.value for state in TransactionState],
                        "example": TransactionState.SENT.value
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
            state=TransactionState.SENT.value,
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
    app.run(debug=config.DEBUG)
