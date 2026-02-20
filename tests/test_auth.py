import pytest

SYSTEM_USER = {"username": "system", "password": "system1234"}


def test_login_system_user(client):
    """Test login as SYSTEM user (created by app initialization)"""
    resp = client.post("/auth/login", json={"username": SYSTEM_USER["username"], "password": SYSTEM_USER["password"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["username"] == SYSTEM_USER["username"]
    assert data["user"]["role"] == "system"


def test_login_invalid_credentials(client):
    """Test login fails with invalid credentials"""
    resp = client.post("/auth/login", json={"username": "system", "password": "wrong_password"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_login_nonexistent_user(client):
    """Test login fails for nonexistent user"""
    resp = client.post("/auth/login", json={"username": "nonexistent", "password": "password123"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_get_current_user(client):
    """Test getting current user info"""
    # First login
    login_resp = client.post("/auth/login", json={"username": "system", "password": "system1234"})
    token = login_resp.json()["access_token"]
    
    # Get current user
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    user = resp.json()
    assert user["username"] == "system"
    assert user["role"] == "system"
    assert user["company_id"] is None  # SYSTEM users have no company
