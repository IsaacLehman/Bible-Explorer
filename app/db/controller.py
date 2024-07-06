"""
    Database controller for the application
"""
from sqlmodel import SQLModel, create_engine, Session
import os

# Define the relative path for the database file
relative_path = "app/db"
sqlite_file_name = "database.db"

# Ensure the directory exists
os.makedirs(relative_path, exist_ok=True)

# Construct the full path to the database file
full_path = os.path.join(relative_path, sqlite_file_name)
sqlite_url = f"sqlite:///{full_path}"

# Create the database engine
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """
    This function creates the database and tables.
    - Must be run after defining all the models.
    return: None
    """
    SQLModel.metadata.create_all(engine)

def get_db():
    """
    This function returns a database session.

    Example usage:
    with get_db() as db:
        db.query(User).all()
    
    return: Session
    """
    return Session(engine)