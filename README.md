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

### Exception Handling Features

The API includes several exception handling features:

1. **Global Exception Handler** - Catches and logs any unexpected exceptions
2. **Request/Response Logging** - Logs all incoming requests and outgoing responses
3. **Exception Handling Decorator** - Provides consistent error handling for route functions
