"""
Database utilities for the Peachtree Bank API.
Provides context managers for database operations.
"""
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

from models import db
from errors import APIError, ResourceNotFoundError


@contextmanager
def db_session():
    """
    Context manager for database sessions.
    
    Provides a transactional scope around a series of operations.
    Automatically commits changes if no exceptions occur,
    or rolls back if an exception is raised.
    
    Usage:
        with db_session() as session:
            # Perform database operations
            session.add(some_object)
            # No need to commit - it's done automatically
    
    Raises:
        APIError: If a database error occurs
    """
    session = db.session
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise APIError(f"Database error: {str(e)}", status_code=500)
    except Exception as e:
        session.rollback()
        raise


@contextmanager
def db_transaction():
    """
    Context manager for database transactions.
    
    Similar to db_session, but specifically for operations that
    need to be treated as a single transaction.
    
    Usage:
        with db_transaction():
            # Perform transactional operations
            account1.balance -= amount
            account2.balance += amount
    
    Raises:
        APIError: If a database error occurs
    """
    try:
        yield
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise APIError(f"Transaction error: {str(e)}", status_code=500)
    except Exception as e:
        db.session.rollback()
        raise


def get_or_404(model, id):
    """
    Get a database object by ID or raise a 404 error.
    
    Args:
        model: The SQLAlchemy model class
        id: The ID to look up
        
    Returns:
        The database object if found
        
    Raises:
        ResourceNotFoundError: If the object is not found
    """
    obj = model.query.get(id)
    if obj is None:
        raise ResourceNotFoundError(f"{model.__name__} with ID {id} not found")
    return obj
