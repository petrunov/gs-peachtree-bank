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

- `NotFound` (404) - The requested resource doesn't exist
- `MethodNotAllowed` (405) - The HTTP method is not allowed for the requested URL
- `InternalServerError` (500) - An unexpected server error occurred

### Custom Exceptions

The API includes custom exception classes that can be raised in route handlers:

- `ResourceNotFoundError` - When a requested resource is not found
- `ValidationError` - When request validation fails
- `AuthorizationError` - When authorization fails
