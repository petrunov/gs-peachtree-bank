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

3. Configure environment (optional):

   ```
   cp .env.example .env
   # Edit .env file with your settings
   ```

4. Initialize and seed the database:

   ```
   python migrations.py
   python seed.py
   ```

5. Run the application:
   ```
   python app.py
   ```

The API will be available at http://127.0.0.1:5000/

## API Endpoints

- `GET /swagger` - HTML page listing all available API endpoints
- `GET /api/health` - Health check endpoint

## Error Handling

The API implements a comprehensive error handling system that provides consistent JSON responses for all errors:

```json
{
  "error": "ErrorType",
  "message": "Description of what went wrong",
  "details": {}
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
6. **Database Integration** - SQLite database with SQLAlchemy ORM
7. **Database Migrations** - Managed with Flask-Migrate
8. **Context Managers** - Safe database transaction handling
9. **CORS Support** - Cross-Origin Resource Sharing for frontend applications
10. **OpenAPI Documentation** - Swagger UI for API exploration and testing
11. **Environment Configuration** - Different configurations for development, testing, and production

## API Documentation

The API provides interactive documentation using Swagger UI, which allows you to explore and test the API endpoints directly from your browser.

### Swagger Documentation

To access the Swagger documentation:

1. Run the application:

   ```
   python app.py
   ```

2. Navigate to the Swagger UI:
   ```
   http://127.0.0.1:5000/swagger/
   ```

The Swagger UI provides:

- A list of all available endpoints
- Detailed information about request parameters and response formats
- The ability to try out API calls directly from the browser
- Schema definitions for request and response objects

## Cross-Origin Resource Sharing (CORS)

The API supports Cross-Origin Resource Sharing (CORS) to allow frontend applications to make requests to the API from different domains.

CORS is enabled for all API routes (`/api/*`) and currently allows requests from any origin (`*`). In a production environment, you should restrict this to specific domains.

To modify CORS settings, update the CORS configuration in `app.py`:

```python
# Allow requests from specific origins
CORS(app, resources={r"/api/*": {"origins": "http://your-frontend-domain.com"}})

# Allow requests from multiple origins
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://your-app.com"]}})
```

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

## Environment Configuration

The API supports different configurations for different environments (development, testing, production). The configuration is managed through the `config.py` file and environment variables.

### Environment Variables

You can customize the configuration by setting environment variables. The easiest way is to create a `.env` file in the project root:

```
# Copy the example file
cp .env.example .env

# Edit the .env file with your settings
```

Available environment variables:

- `FLASK_ENV` - Environment name (development, testing, production)
- `SECRET_KEY` - Secret key for session management
- `DATABASE_URL` - Database connection URL
- `RATELIMIT_STORAGE_URI` - Storage URI for rate limiting
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Context Managers

The API provides context managers for safe database operations.
These context managers ensure that database operations are performed safely:

- Automatically commit changes when operations succeed
- Automatically roll back changes when errors occur
- Convert database errors to consistent API error responses
