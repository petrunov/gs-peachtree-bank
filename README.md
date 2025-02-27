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
- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Create a new transaction

### Transaction Endpoints

#### List Transactions

The GET endpoint allows you to retrieve a list of all transactions:

```
GET /api/transactions
GET /api/transactions?limit=10&offset=0
```

This endpoint:

1. Returns a list of all transactions in the database
2. Supports pagination with limit and offset parameters
3. Orders transactions by date (newest first)
4. Returns a maximum of 100 transactions per request

#### Create Transaction

The POST endpoint allows you to create new transactions between accounts:

```
POST /api/transactions
Content-Type: application/json

{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": "100.00",
  "beneficiary": "John Doe",
  "description": "Monthly rent payment"
}
```

This will:

1. Validate the request data
2. Check if both accounts exist
3. Verify sufficient funds in the source account
4. Create a transaction record with "pending" state
5. Update the balances of both accounts
6. Return the created transaction with a 201 status code

All of these operations are performed within a transaction context manager to ensure atomicity.

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
6. **Database Integration** - SQLite database with SQLAlchemy ORM
7. **Database Migrations** - Managed with Flask-Migrate
8. **Context Managers** - Safe database transaction handling
9. **CORS Support** - Cross-Origin Resource Sharing for frontend applications
10. **OpenAPI Documentation** - Swagger UI for API exploration and testing

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

## Database Setup

The API uses SQLite with SQLAlchemy ORM for data persistence:

1. **Initialize the database**:

   ```
   python migrations.py
   ```

2. **Seed the database with sample data**:
   ```
   python seed.py
   ```

### Database Models

- **Account** - Bank accounts with account number, name, and balance
- **Transaction** - Money transfers between accounts with amount, beneficiary, and state

### Context Managers

The API provides context managers for safe database operations:

```python
# Using db_session for general database operations
with db_session() as session:
    new_account = Account(
        account_number="1234567890",
        account_name="John Doe Checking",
        balance=1000.00
    )
    session.add(new_account)
    # No need to commit - it's done automatically

# Using db_transaction for operations that must be atomic
with db_transaction():
    # Transfer money between accounts
    transaction = Transaction(
        amount=100.00,
        from_account_id=1,
        to_account_id=2,
        beneficiary="Jane Smith",
        state="pending"
    )
    db.session.add(transaction)

    # Update account balances
    from_account.balance -= 100.00
    to_account.balance += 100.00
```

These context managers ensure that database operations are performed safely:

- Automatically commit changes when operations succeed
- Automatically roll back changes when errors occur
- Convert database errors to consistent API error responses
