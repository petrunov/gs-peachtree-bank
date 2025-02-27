"""
Validation schemas for the Peachtree Bank API.
Defines schemas for request validation using marshmallow.
"""
from marshmallow import Schema, fields, validate, ValidationError
from decimal import Decimal


class TransactionSchema(Schema):
    """Schema for validating transaction data."""
    from_account_id = fields.Integer(required=True, validate=validate.Range(min=1))
    to_account_id = fields.Integer(required=True, validate=validate.Range(min=1))
    amount = fields.Decimal(required=True, validate=validate.Range(min=Decimal('0.01')))
    beneficiary = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=200))


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
