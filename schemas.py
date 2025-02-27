"""
Validation schemas for the Peachtree Bank API.
Defines schemas for request validation using marshmallow.
"""
from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from decimal import Decimal
import re


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
    beneficiary = fields.String(
        required=True, 
        validate=[
            validate.Length(min=1, max=100, error="Beneficiary name must be between 1 and 100 characters"),
            validate.Regexp(r'^[a-zA-Z0-9 ]+$', error="Beneficiary name can only contain letters, numbers, and spaces")
        ]
    )
    description = fields.String(
        validate=validate.Length(max=200, error="Description cannot exceed 200 characters")
    )
    
    @validates_schema
    def validate_different_accounts(self, data, **kwargs):
        """Validate that source and destination accounts are different."""
        if data.get('from_account_id') == data.get('to_account_id'):
            raise ValidationError("Source and destination accounts must be different", "to_account_id")


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
        from errors import ValidationError as APIValidationError
        raise APIValidationError(
            message="Request validation failed",
            payload=err.messages
        )
