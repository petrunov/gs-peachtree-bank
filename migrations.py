"""
Migration script for the Peachtree Bank API.
Initializes and creates database migrations.
"""
import os
import subprocess
from app import app, db


def init_migrations():
    """Initialize database migrations."""
    print("Initializing migrations...")
    
    # Check if migrations directory already exists
    if os.path.exists('migrations'):
        print("Migrations already initialized.")
        return
    
    # Initialize migrations
    with app.app_context():
        try:
            subprocess.run(['flask', 'db', 'init'], check=True)
            print("Migrations initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error initializing migrations: {e}")
            return


def create_migration():
    """Create a new migration."""
    print("Creating migration...")
    
    # Create migration
    with app.app_context():
        try:
            subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration'], check=True)
            print("Migration created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating migration: {e}")
            return


def apply_migration():
    """Apply the migration to the database."""
    print("Applying migration...")
    
    # Apply migration
    with app.app_context():
        try:
            subprocess.run(['flask', 'db', 'upgrade'], check=True)
            print("Migration applied successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error applying migration: {e}")
            return


if __name__ == "__main__":
    # Set Flask app environment variable
    os.environ['FLASK_APP'] = 'app.py'
    
    # Initialize migrations
    init_migrations()
    
    # Create migration
    create_migration()
    
    # Apply migration
    apply_migration()
    
    print("Migration process completed.")
