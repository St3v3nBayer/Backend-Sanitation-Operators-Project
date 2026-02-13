import pytest
from fastapi.testclient import TestClient


def test_list_tenants_forbidden(client):
    """Test que usuario normal NO puede listar tenants"""
    # Login como usuario normal (registrado en conftest)
    resp = client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    
    # Intentar listar tenants (debe fallar con 403)
    resp = client.get("/admin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_list_tenants_admin(client):
    """Test que usuario SYSTEM puede listar tenants"""
    # Login como admin (creado en conftest)
    resp = client.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    
    # Listar tenants
    resp = client.get("/admin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Debe tener al menos el tenant "default"
    assert len(data) >= 1
    assert data[0]["name"] == "default"


def test_create_tenant_admin(client):
    """Test que usuario SYSTEM puede crear tenants"""
    # Login como admin
    resp = client.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
    token = resp.json()["access_token"]
    
    # Crear tenant
    resp = client.post(
        "/admin/tenants",
        json={
            "name": "newtenant",
            "nit": "123456789",
            "database_url": "postgresql://user:pass@localhost/dbname"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "newtenant"
    assert data["nit"] == "123456789"
    assert data["active"] == True


def test_get_tenant_admin(client):
    """Test que usuario SYSTEM puede obtener tenant específico"""
    # Login como admin
    resp = client.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
    token = resp.json()["access_token"]
    
    # Crear un tenant
    resp = client.post(
        "/admin/tenants",
        json={
            "name": "gettenant",
            "nit": "111111111",
            "database_url": "postgresql://user:pass@localhost/dbget"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    tenant_id = resp.json()["id"]
    
    # Obtener ese tenant
    resp = client.get(f"/admin/tenants/{tenant_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == tenant_id
    assert data["name"] == "gettenant"


def test_update_tenant_admin(client):
    """Test que usuario SYSTEM puede actualizar tenants"""
    # Login como admin
    resp = client.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
    token = resp.json()["access_token"]
    
    # Crear tenant para actualizar
    resp = client.post(
        "/admin/tenants",
        json={
            "name": "updatetenant",
            "nit": "222222222",
            "database_url": "postgresql://user:pass@localhost/dbupdate"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    tenant_id = resp.json()["id"]
    
    # Actualizar tenant
    resp = client.put(
        f"/admin/tenants/{tenant_id}",
        json={"active": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["active"] == False


def test_delete_tenant_admin(client):
    """Test que usuario SYSTEM puede eliminar tenants"""
    # Login como admin
    resp = client.post("/auth/login", json={"username": "systemuser", "password": "system1234"})
    token = resp.json()["access_token"]
    
    # Crear tenant para eliminar
    resp = client.post(
        "/admin/tenants",
        json={
            "name": "tenantdelete",
            "nit": "987654321",
            "database_url": "postgresql://user:pass@localhost/dbdelete"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    tenant_id = resp.json()["id"]
    
    # Eliminar tenant
    resp = client.delete(f"/admin/tenants/{tenant_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204
