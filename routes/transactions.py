"""
Transaction endpoints for the Peachtree Bank API.
"""
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from sqlalchemy import or_, desc, asc
from decimal import Decimal

from models import Transaction, Account, TransactionState, TransactionType, db
from schemas import validate_request, TransactionSchema, TransactionQuerySchema, TransactionUpdateSchema
from errors import ValidationError
from db import db_transaction, get_or_404

# Create blueprint
transactions_bp = Blueprint('transactions', __name__, url_prefix='/api')

@transactions_bp.route('/transactions', methods=['GET'])
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
                            "enum": [type.value for type in TransactionType],
                            "example": TransactionType.TRANSACTION.value
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
        query = query.join(Account, Transaction.to_account_id == Account.id).filter(
            or_(
                Account.account_name.ilike(search_term),
                Transaction.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == 'date':
        sort_column = Transaction.date
    elif sort_by == 'amount':
        sort_column = Transaction.amount
    elif sort_by == 'beneficiary':
        # Join with Account table to sort by account_name
        query = query.join(Account, Transaction.to_account_id == Account.id)
        sort_column = Account.account_name
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

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
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
                        "enum": [type.value for type in TransactionType],
                        "example": TransactionType.TRANSACTION.value
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

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['PATCH'])
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
                        "enum": [type.value for type in TransactionType],
                        "example": TransactionType.TRANSACTION.value
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
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")
    
    validated_data = validate_request(TransactionUpdateSchema(), data)
    
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

@transactions_bp.route('/transactions', methods=['POST'])
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
                "required": ["from_account_id", "to_account_id", "amount", "description"],
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
                    "description": {
                        "type": "string",
                        "enum": [type.value for type in TransactionType],
                        "example": TransactionType.TRANSACTION.value
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
                        "enum": [type.value for type in TransactionType],
                        "example": TransactionType.TRANSACTION.value
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
    - amount: Amount of the transaction
    - description: Transaction type (Card Payments, Transaction, Online transfer)
    
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
    
    amount = Decimal(str(validated_data['amount']))
    
    with db_transaction():
        # Create transaction record
        transaction = Transaction(
            date=validated_data.get('date'),
            amount=amount,
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            state=TransactionState.SENT.value,
            description=validated_data.get('description', '')
        )
        db.session.add(transaction)
        
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
