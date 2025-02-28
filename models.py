"""
Database models for the Peachtree Bank API.
"""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SQLAlchemyEnum

db = SQLAlchemy()


class TransactionState(str, Enum):
    """Enum representing the possible states of a transaction."""
    SENT = 'sent'
    RECEIVED = 'received'
    PAID = 'paid'
    
    def __str__(self):
        return self.value


class TransactionType(str, Enum):
    """Enum representing the possible types of a transaction."""
    CARD_PAYMENT = 'Card Payments'
    TRANSACTION = 'Transaction'
    ONLINE_TRANSFER = 'Online transfer'
    
    def __str__(self):
        return self.value


class Account(db.Model):
    """Account model representing bank accounts."""
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(10), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
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
    state = db.Column(SQLAlchemyEnum(TransactionState), default=TransactionState.SENT)
    description = db.Column(SQLAlchemyEnum(TransactionType), default=TransactionType.TRANSACTION, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def beneficiary(self):
        """Get the beneficiary name from the to_account relationship."""
        return self.to_account.account_name if self.to_account else None
    
    def __repr__(self):
        return f'<Transaction {self.id} {self.amount} {self.state}>'
