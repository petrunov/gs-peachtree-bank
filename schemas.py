"""
Validation schemas for the Peachtree Bank API.
Defines utility functions for request validation using marshmallow.
"""
from marshmallow import ValidationError


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
