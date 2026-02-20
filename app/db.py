import os
import time
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.exc import OperationalError

# Single database connection for the company
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
engine = create_engine(DATABASE_URL, echo=False)


def init_db(retries: int = 10, delay: int = 2):
    """
    Initialize database - create all tables for single company.
    Called once at startup.
    """
    for attempt in range(1, retries + 1):
        try:
            # Create all tables
            SQLModel.metadata.create_all(engine)
            print("[Startup] Database initialized successfully")
            return
        except OperationalError as e:
            if attempt == retries:
                raise
            print(f"Database not ready (attempt {attempt}/{retries}), retrying in {delay}s...")
            time.sleep(delay)


def get_session():
    """Get database session for current company"""
    with Session(engine) as session:
        yield session
