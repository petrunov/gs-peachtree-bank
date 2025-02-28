"""
Validation schemas for the Peachtree Bank API.
Defines schemas for request validation using marshmallow.
"""
import re
from decimal import Decimal

from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from models import TransactionState, TransactionType
from errors import ValidationError as APIValidationError


class AccountSchema(Schema):
    """Schema for validating account data."""
    account_number = fields.String(
        required=True, 
        validate=[
            validate.Length(equal=10, error="Account number must be exactly 10 digits"),
            validate.Regexp(r'^\d+$', error="Account number must contain only digits")
        ]
    )
    account_name = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=100, error="Account name must be between 3 and 100 characters"),
            validate.Regexp(r'^[a-zA-Z0-9 ]+$', error="Account name can only contain letters, numbers, and spaces")
        ]
    )
    balance = fields.Decimal(
        places=2,
        as_string=True,
        validate=validate.Range(min=0, error="Balance cannot be negative")
    )
    currency = fields.String(
        validate=validate.Length(equal=3, error="Currency code must be 3 characters"),
        default="USD"
    )


class TransactionSchema(Schema):
    """Schema for validating transaction data."""
    from_account_id = fields.Integer(
        required=True, 
        validate=validate.Range(min=1, error="Invalid source account ID")
    )
    to_account_id = fields.Integer(
        required=True, 
        validate=validate.Range(min=1, error="Invalid destination account ID")
    )
    amount = fields.Decimal(
        required=True, 
        places=2,
        as_string=True,
        validate=validate.Range(min=Decimal('0.01'), error="Amount must be greater than zero")
    )
    description = fields.String(
        required=True,
        validate=validate.OneOf(
            [type.value for type in TransactionType],
            error=f"Description must be one of: {', '.join([type.value for type in TransactionType])}"
        )
    )
    state = fields.String(
        validate=validate.OneOf(
            [state.value for state in TransactionState],
            error=f"State must be one of: {', '.join([state.value for state in TransactionState])}"
        )
    )
    
    @validates_schema
    def validate_different_accounts(self, data, **kwargs):
        """Validate that source and destination accounts are different."""
        if data.get('from_account_id') == data.get('to_account_id'):
            raise ValidationError("Source and destination accounts must be different", "to_account_id")


class TransactionUpdateSchema(Schema):
    """Schema for validating transaction update data."""
    state = fields.String(
        required=True,
        validate=validate.OneOf(
            [state.value for state in TransactionState],
            error=f"State must be one of: {', '.join([state.value for state in TransactionState])}"
        )
    )


class AccountQuerySchema(Schema):
    """Schema for validating account query parameters."""
    limit = fields.Integer(
        validate=validate.Range(min=1, max=100, error="Limit must be between 1 and 100"),
        missing=100
    )
    offset = fields.Integer(
        validate=validate.Range(min=0, error="Offset cannot be negative"),
        missing=0
    )
    sort_by = fields.String(
        validate=validate.OneOf(
            ["account_number", "account_name", "balance", "created_at"],
            error="Sort field must be one of: account_number, account_name, balance, created_at"
        ),
        missing="account_number"
    )
    sort_order = fields.String(
        validate=validate.OneOf(
            ["asc", "desc"],
            error="Sort order must be one of: asc, desc"
        ),
        missing="asc"
    )


class TransactionQuerySchema(Schema):
    """Schema for validating transaction query parameters."""
    limit = fields.Integer(
        validate=validate.Range(min=1, max=100, error="Limit must be between 1 and 100"),
        missing=100
    )
    offset = fields.Integer(
        validate=validate.Range(min=0, error="Offset cannot be negative"),
        missing=0
    )
    sort_by = fields.String(
        validate=validate.OneOf(
            ["date", "amount", "beneficiary"],
            error="Sort field must be one of: date, amount, beneficiary"
        ),
        missing="date"
    )
    sort_order = fields.String(
        validate=validate.OneOf(
            ["asc", "desc"],
            error="Sort order must be one of: asc, desc"
        ),
        missing="desc"
    )
    search = fields.String(
        validate=validate.Length(max=100, error="Search query cannot exceed 100 characters")
    )


def sanitize_string(value):
    """
    Sanitize a string value to prevent XSS and other injection attacks.
    
    Args:
        value: The string to sanitize
        
    Returns:
        str: The sanitized string
    """
    if not value:
        return value
        
    # Remove any HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    
    # Remove any script tags and their contents
    value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.DOTALL)
    
    # Remove any potentially dangerous attributes
    value = re.sub(r'on\w+=".*?"', '', value)
    
    return value


def validate_request(schema, request_data):
    """
    Validate request data against a schema.
    
    Args:
        schema: The marshmallow schema to validate against
        request_data: The data to validate
        
    Returns:
        dict: The validated data
        
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize string inputs to prevent injection attacks
    if isinstance(request_data, dict):
        for key, value in request_data.items():
            if isinstance(value, str):
                request_data[key] = sanitize_string(value)
    
    try:
        # Validate and return the data
        return schema.load(request_data)
    except ValidationError as err:
        # Re-raise as our custom ValidationError
        raise APIValidationError(
            message="Request validation failed",
            payload=err.messages
        )
