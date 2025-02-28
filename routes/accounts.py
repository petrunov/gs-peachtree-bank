"""
Account endpoints for the Peachtree Bank API.
"""
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from sqlalchemy import desc, asc

from models import Account
from schemas import validate_request, AccountSchema, AccountQuerySchema
from db import get_or_404

# Create blueprint
accounts_bp = Blueprint('accounts', __name__, url_prefix='/api')

@accounts_bp.route('/accounts', methods=['GET'])
@swag_from({
    "tags": ["Accounts"],
    "summary": "Get all accounts",
    "description": "Returns a list of all accounts in the database",
    "parameters": [
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "description": "Maximum number of accounts to return",
            "default": 100,
            "required": False
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "description": "Number of accounts to skip",
            "default": 0,
            "required": False
        },
        {
            "name": "sort_by",
            "in": "query",
            "type": "string",
            "description": "Field to sort by",
            "enum": ["account_number", "account_name", "created_at"],
            "default": "account_number",
            "required": False
        },
        {
            "name": "sort_order",
            "in": "query",
            "type": "string",
            "description": "Sort order",
            "enum": ["asc", "desc"],
            "default": "asc",
            "required": False
        }
    ],
    "responses": {
        "200": {
            "description": "List of accounts",
            "schema": {
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
                            "example": "Checking Account"
                        },
                        "currency": {
                            "type": "string",
                            "example": "USD"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-02-27T11:00:00.000Z"
                        },
                        "updated_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-02-27T11:00:00.000Z"
                        }
                    }
                }
            }
        }
    }
})
def get_accounts():
    """Get all accounts.
    
    Returns a list of all accounts in the database.
    
    Query parameters:
    - limit: Maximum number of accounts to return (default: 100)
    - offset: Number of accounts to skip (default: 0)
    - sort_by: Field to sort by (account_number, account_name, created_at) (default: account_number)
    - sort_order: Sort order (asc, desc) (default: asc)
    """
    # Validate query parameters
    query_params = {}
    for param in ['limit', 'offset', 'sort_by', 'sort_order']:
        if request.args.get(param):
            query_params[param] = request.args.get(param)
    
    # Validate and get parameters
    validated_params = validate_request(AccountQuerySchema(), query_params)
    limit = validated_params.get('limit', 100)
    offset = validated_params.get('offset', 0)
    sort_by = validated_params.get('sort_by', 'account_number')
    sort_order = validated_params.get('sort_order', 'asc')
    
    # Start building the query
    query = Account.query
    
    # Apply sorting
    if sort_by == 'account_number':
        sort_column = Account.account_number
    elif sort_by == 'account_name':
        sort_column = Account.account_name
    elif sort_by == 'created_at':
        sort_column = Account.created_at
    else:
        sort_column = Account.account_number
    
    if sort_order.lower() == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Apply pagination
    accounts = query.limit(limit).offset(offset).all()
    
    # Format the response
    result = []
    for account in accounts:
        result.append({
            "id": account.id,
            "account_number": account.account_number,
            "account_name": account.account_name,
            "currency": account.currency,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat()
        })
    
    # Return the accounts
    return jsonify(result)


@accounts_bp.route('/accounts/<int:account_id>', methods=['GET'])
@swag_from({
    "tags": ["Accounts"],
    "summary": "Get account details",
    "description": "Returns details for a specific account",
    "parameters": [
        {
            "name": "account_id",
            "in": "path",
            "type": "integer",
            "description": "ID of the account to retrieve",
            "required": True
        }
    ],
    "responses": {
        "200": {
            "description": "Account details",
            "schema": {
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
                        "example": "Checking Account"
                    },
                    "currency": {
                        "type": "string",
                        "example": "USD"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2025-02-27T11:00:00.000Z"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2025-02-27T11:00:00.000Z"
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
def get_account(account_id):
    """Get a specific account by ID.
    
    Returns details for a specific account.
    
    Path parameters:
    - account_id: ID of the account to retrieve
    """
    # Get the account
    account = get_or_404(Account, account_id)
    
    # Return the account details
    return jsonify({
        "id": account.id,
        "account_number": account.account_number,
        "account_name": account.account_name,
        "currency": account.currency,
        "created_at": account.created_at.isoformat(),
        "updated_at": account.updated_at.isoformat()
    })
