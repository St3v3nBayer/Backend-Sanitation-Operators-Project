import pytest
from fastapi.testclient import TestClient


SYSTEM_USER = {"username": "system", "password": "system1234"}


def test_health_check(client):
    """Test health check endpoint (public)"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["mode"] == "single-tenant"


def test_system_user_can_list_companies(client):
    """Test that SYSTEM user can list companies"""
    # Login as SYSTEM user
    resp = client.post("/auth/login", json=SYSTEM_USER)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    
    # List companies (should work for SYSTEM user)
    resp = client.get("/companies", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    companies = resp.json()
    assert isinstance(companies, list)
    # Should include the default company
    assert len(companies) >= 1
    assert companies[0]["name"] == "Default Company"


def test_system_user_can_create_company(client):
    """Test that SYSTEM user can create companies"""
    # Login as SYSTEM user
    resp = client.post("/auth/login", json=SYSTEM_USER)
    token = resp.json()["access_token"]
    
    # Create a company
    new_company = {
        "name": "Test Company",
        "nit": "1234567890"
    }
    resp = client.post(
        "/companies",
        json=new_company,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == new_company["name"]
    assert data["nit"] == new_company["nit"]


def test_unauthenticated_cannot_list_companies(client):
    """Test that unauthenticated requests cannot list companies"""
    resp = client.get("/companies")
    # Should redirect or require auth (307 or 401)
    assert resp.status_code in [307, 401, 403]


def test_system_user_role_in_token(client):
    """Test that SYSTEM user has correct role in token"""
    # Login as SYSTEM user
    resp = client.post("/auth/login", json=SYSTEM_USER)
    assert resp.status_code == 200
    user_data = resp.json()["user"]
    
    # Verify role and company_id
    assert user_data["role"] == "system"
    assert user_data["company_id"] is None
    assert user_data["active"] is True
