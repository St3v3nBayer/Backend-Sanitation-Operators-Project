import pytest

ADMIN = {"username": "systemuser", "password": "system1234", "role": "system"}
USER = {"username": "testuser", "password": "testpass123", "email": "test@user.com"}


def test_login_admin(client):
    # login with seeded admin
    resp = client.post("/auth/login", json={"username": ADMIN["username"], "password": ADMIN["password"]})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token


def test_register_user(client):
    # login as admin
    resp = client.post("/auth/login", json={"username": ADMIN["username"], "password": ADMIN["password"]})
    token = resp.json()["access_token"]
    # register new user (with different name since testuser already exists)
    resp = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "newpass123", "email": "new@user.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code != 200:
        print(f"Error response: {resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@user.com"


def test_login_user(client):
    # Login with the testuser pre-seeded in conftest
    resp = client.post("/auth/login", json={"username": USER["username"], "password": USER["password"]})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token


def test_register_user_forbidden(client):
    # login as normal user
    resp = client.post("/auth/login", json={"username": USER["username"], "password": USER["password"]})
    token = resp.json()["access_token"]
    # try to register another user (should be forbidden)
    resp = client.post(
        "/auth/register",
        json={"username": "other", "password": "otherpass", "email": "other@user.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403
