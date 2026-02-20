import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import engine
from sqlmodel import Session, SQLModel, delete
from app.models.user import User
from app.models.company import Company
from app.models.audit_log import AuditLog

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean database before and after each test"""
    # BEFORE test: Clean everything in correct order (respecting FK constraints)
    with Session(engine) as session:
        session.exec(delete(AuditLog))  # Delete first (FK references User)
        session.exec(delete(User))
        session.exec(delete(Company))
        session.commit()
    
    yield
    
    # AFTER test: Clean everything in correct order (respecting FK constraints)
    with Session(engine) as session:
        session.exec(delete(AuditLog))  # Delete first (FK references User)
        session.exec(delete(User))
        session.exec(delete(Company))
        session.commit()

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
