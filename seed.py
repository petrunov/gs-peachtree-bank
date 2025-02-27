"""
Seed script for the Peachtree Bank API.
Populates the database with initial data.
"""
import random
from datetime import datetime, timedelta
from app import app, db
from models import Account, Transaction, TransactionState


def generate_account_number():
    """Generate a random 10-digit account number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])


def seed_database():
    """Seed the database with initial data."""
    print("Seeding database...")
    
    # Create accounts
    accounts = [
        Account(
            account_number=generate_account_number(),
            account_name="John Doe Checking",
            balance=5000.00,
            currency="USD"
        ),
        Account(
            account_number=generate_account_number(),
            account_name="Jane Smith Savings",
            balance=15000.00,
            currency="USD"
        ),
        Account(
            account_number=generate_account_number(),
            account_name="Michael Johnson Business",
            balance=25000.00,
            currency="USD"
        ),
        Account(
            account_number=generate_account_number(),
            account_name="Sarah Williams Personal",
            balance=3500.00,
            currency="USD"
        ),
        Account(
            account_number=generate_account_number(),
            account_name="Robert Brown Investment",
            balance=50000.00,
            currency="USD"
        )
    ]
    
    db.session.add_all(accounts)
    db.session.commit()
    print(f"Added {len(accounts)} accounts")
    
    # Create transactions
    transactions = []
    
    # Transaction states
    states = [state.value for state in TransactionState]
    
    # Generate transactions between accounts
    for _ in range(10):  # Reduced by half
        # Select random from and to accounts
        from_account = random.choice(accounts)
        to_account = random.choice([a for a in accounts if a != from_account])
        
        # Random date in the last 30 days
        days_ago = random.randint(0, 30)
        transaction_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Random amount between $10 and $500
        amount = round(random.uniform(10, 500), 2)
        
        # Random state with weighted probability
        state = random.choices(
            states, 
            weights=[0.4, 0.3, 0.3],  # 40% sent, 30% received, 30% paid
            k=1
        )[0]
        
        # Random description
        descriptions = [
            "Monthly transfer",
            "Bill payment",
            "Rent payment",
            "Salary deposit",
            "Investment transfer",
            "Loan repayment",
            "Subscription payment",
            "Insurance premium"
        ]
        description = random.choice(descriptions)
        
        # Create transaction
        transaction = Transaction(
            date=transaction_date,
            amount=amount,
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            beneficiary=to_account.account_name.split()[0] + " " + to_account.account_name.split()[1],
            state=state,
            description=description
        )
        transactions.append(transaction)
    
    db.session.add_all(transactions)
    db.session.commit()
    print(f"Added {len(transactions)} transactions")
    
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if database is already seeded
        if Account.query.count() == 0:
            seed_database()
        else:
            print("Database already contains data. Skipping seed.")
