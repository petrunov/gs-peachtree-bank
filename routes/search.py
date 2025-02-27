"""
Search endpoints for the Peachtree Bank API.
"""
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from sqlalchemy import or_

from models import Account, Transaction
from errors import ValidationError

# Create blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api')

@search_bp.route('/search', methods=['GET'])
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
