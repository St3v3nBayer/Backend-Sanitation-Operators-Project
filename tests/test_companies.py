
import pytest

COMPANY = {"name": "ACME", "nit": "123456789", "address": "Cra 1 #2-3", "phone": "3001234567", "email": "acme@company.com"}

@pytest.fixture(scope="function")
def admin_token(client):
    resp = client.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
    return resp.json()["access_token"]


def test_create_company(client, admin_token):
    resp = client.post("/companies", json=COMPANY, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == COMPANY["name"]
    assert data["nit"] == COMPANY["nit"]


def test_list_companies_after_create(client, admin_token):
    # Create a company first
    resp = client.post("/companies", json=COMPANY, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    # Then list
    resp = client.get("/companies", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    companies = resp.json()
    assert any(c["name"] == COMPANY["name"] for c in companies)


def test_update_company(client, admin_token):
    # Create company first
    resp = client.post("/companies", json=COMPANY, headers={"Authorization": f"Bearer {admin_token}"})
    company_id = resp.json()["id"]
    # Then update
    resp = client.put(f"/companies/{company_id}", json={"address": "Nueva direccion"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["address"] == "Nueva direccion"


def test_delete_company(client, admin_token):
    # Create company first
    resp = client.post("/companies", json=COMPANY, headers={"Authorization": f"Bearer {admin_token}"})
    company_id = resp.json()["id"]
    # Then delete
    resp = client.delete(f"/companies/{company_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204


def test_list_companies_empty(client, admin_token):
    resp = client.get("/companies", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 0
