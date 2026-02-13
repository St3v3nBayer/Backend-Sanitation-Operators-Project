import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import engine, central_engine
from sqlmodel import Session, SQLModel, delete
from app.models.user import User
from app.models.company import Company
from app.models.tenant import Tenant

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean database before and after each test"""
    # BEFORE test: Clean everything
    with Session(engine) as session:
        session.exec(delete(User))
        session.exec(delete(Company))
        session.commit()
    
    with Session(central_engine) as session:
        session.exec(delete(User))
        session.exec(delete(Tenant))
        session.commit()
    
    yield
    
    # AFTER test: Clean everything
    with Session(engine) as session:
        session.exec(delete(User))
        session.exec(delete(Company))
        session.commit()
    
    with Session(central_engine) as session:
        session.exec(delete(User))
        session.exec(delete(Tenant))
        session.commit()

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        # Seed system user for each test
        c.post("/auth/init", json={"username": "systemuser", "password": "system1234"})
        
        # Register a normal test user
        admin_login = c.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
        admin_token = admin_login.json()["access_token"]
        c.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123", "email": "test@user.com"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        yield c
