"""
Main application file for the Peachtree Bank API.
"""
import logging
from flask import Flask, jsonify, render_template, request
from errors import register_error_handlers, ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from schemas import validate_request, TransactionSchema
from flask_migrate import Migrate
from models import db, Account, Transaction
from db import db_transaction, get_or_404
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peachtree.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Register error handlers
register_error_handlers(app)

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Request/Response logging middleware
@app.before_request
def log_request():
    """Log the incoming request"""
    app.logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    """Log the response"""
    app.logger.info(f"Response: {response.status_code}")
    return response

@app.route('/', methods=['GET'])
@limiter.exempt  # No rate limit for documentation page
def index():
    """Root endpoint that displays available API endpoints."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
@limiter.limit("10 per minute")  # Custom rate limit for health endpoint
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({"status": "healthy"})


@app.route('/api/transactions', methods=['GET'])
@limiter.limit("30 per minute")
def get_transactions():
    """Get all transactions.
    
    Returns a list of all transactions in the database.
    
    Query parameters:
    - limit: Maximum number of transactions to return (default: 100)
    - offset: Number of transactions to skip (default: 0)
    """
    # Get query parameters
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Limit the maximum number of transactions to return
    if limit > 100:
        limit = 100
    
    # Query transactions with pagination
    transactions = Transaction.query.order_by(Transaction.date.desc()).limit(limit).offset(offset).all()
    
    # Format the response
    result = []
    for transaction in transactions:
        result.append({
            "id": transaction.id,
            "date": transaction.date.isoformat(),
            "amount": str(transaction.amount),
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "beneficiary": transaction.beneficiary,
            "state": transaction.state,
            "description": transaction.description
        })
    
    # Return the transactions
    return jsonify(result)


@app.route('/api/transactions', methods=['POST'])
@limiter.limit("30 per minute")
def create_transaction():
    """Create a new transaction.
    
    Accepts JSON with:
    - from_account_id: ID of the source account
    - to_account_id: ID of the destination account
    - amount: Amount to transfer
    - beneficiary: Name of the beneficiary
    - description: Optional description
    
    Returns the created transaction.
    """
    # Get JSON data from request
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")
    
    # Validate the request data
    validated_data = validate_request(TransactionSchema(), data)
    
    # Get the accounts
    from_account = get_or_404(Account, validated_data['from_account_id'])
    to_account = get_or_404(Account, validated_data['to_account_id'])
    
    # Check if accounts are different
    if from_account.id == to_account.id:
        raise ValidationError("Source and destination accounts must be different")
    
    # Check if source account has sufficient funds
    amount = Decimal(str(validated_data['amount']))
    if from_account.balance < amount:
        raise ValidationError("Insufficient funds in source account")
    
    # Create the transaction
    with db_transaction():
        # Create transaction record
        transaction = Transaction(
            date=validated_data.get('date'),
            amount=amount,
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            beneficiary=validated_data['beneficiary'],
            state='pending',
            description=validated_data.get('description', '')
        )
        db.session.add(transaction)
        
        # Update account balances
        from_account.balance -= amount
        to_account.balance += amount
        
        # Commit is handled by the context manager
    
    # Return the created transaction
    return jsonify({
        "id": transaction.id,
        "date": transaction.date.isoformat(),
        "amount": str(transaction.amount),
        "from_account_id": transaction.from_account_id,
        "to_account_id": transaction.to_account_id,
        "beneficiary": transaction.beneficiary,
        "state": transaction.state,
        "description": transaction.description
    }), 201


if __name__ == '__main__':
    app.run(debug=True)
