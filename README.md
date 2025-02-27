# Peachtree Bank REST API

A simple REST API built with Flask for Peachtree Bank.

## Setup

1. Create and activate a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

The API will be available at http://127.0.0.1:5000/

## API Endpoints

- `GET /` - HTML page listing all available API endpoints
- `GET /api/health` - Health check endpoint

## Error Handling

The API implements a comprehensive error handling system that provides consistent JSON responses for all errors:

```json
{
  "error": "ErrorType",
  "message": "Description of what went wrong",
  "details": {} // Optional additional information
}
```

### Error Types

- `ResourceNotFoundError` (404) - When a requested resource is not found
- `ValidationError` (400) - When request validation fails
- `AuthorizationError` (401) - When authorization fails
- `MethodNotAllowed` (405) - The HTTP method is not allowed for the requested URL
- `InternalServerError` (500) - An unexpected server error occurred
- `UnexpectedError` (500) - Catch-all for any unhandled exceptions

### API Features

The API includes several features for robustness and security:

1. **Global Exception Handler** - Catches and logs any unexpected exceptions
2. **Request/Response Logging** - Logs all incoming requests and outgoing responses
3. **Exception Handling Decorator** - Provides consistent error handling for route functions
4. **Rate Limiting** - Prevents abuse by limiting the number of requests clients can make
5. **Request Validation** - Validates incoming request data using Marshmallow schemas

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage:

- Default limits: 200 requests per day, 50 requests per hour
- Documentation page (`/`): No rate limit
- Health check endpoint (`/api/health`): 10 requests per minute

When a client exceeds the rate limit, the API returns a 429 Too Many Requests response:

```json
{
  "error": "RateLimitExceeded",
  "message": "Rate limit exceeded. Please try again later."
}
```

## Request Validation

The API uses Marshmallow schemas to validate incoming request data. This ensures that all data conforms to expected formats and constraints before processing.

When validation fails, the API returns a 400 Bad Request response with details about the validation errors:

```json
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "details": {
    "field_name": ["Error message for this field"]
  }
}
```

Validation is implemented using:

- **Marshmallow schemas** - Define the expected structure and constraints for request data
- **Custom validation functions** - Handle complex validation logic
- **Integration with error handling** - Provides consistent error responses for validation failures
