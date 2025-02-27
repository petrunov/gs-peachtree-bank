"""
Database models for the Peachtree Bank API.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Account(db.Model):
    """Account model representing bank accounts."""
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(10), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    currency = db.Column(db.String(3), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    outgoing_transactions = db.relationship(
        'Transaction', 
        backref='from_account', 
        lazy=True,
        foreign_keys='Transaction.from_account_id'
    )
    incoming_transactions = db.relationship(
        'Transaction',
        backref='to_account',
        lazy=True,
        foreign_keys='Transaction.to_account_id'
    )
    
    def __repr__(self):
        return f'<Account {self.account_number} ({self.account_name})>'


class Transaction(db.Model):
    """Transaction model representing money transfers."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    beneficiary = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id} {self.amount} {self.state}>'
