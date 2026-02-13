from typing import List, Optional
from sqlmodel import Session
from ..models.tenant import Tenant
from ..repositories.tenant_repository import TenantRepository


def list_tenants(session: Optional[Session] = None) -> List[Tenant]:
    """Lista todos los tenants"""
    repo = TenantRepository(session=session)
    return repo.get_all()


def get_tenant(tenant_id: int, session: Optional[Session] = None) -> Optional[Tenant]:
    """Obtiene tenant por ID"""
    repo = TenantRepository(session=session)
    return repo.get_by_id(tenant_id)


def create_tenant(name: str, nit: str, database_url: str, session: Optional[Session] = None) -> Tenant:
    """
    Crea nuevo tenant.
    
    Validaciones:
    - Nombre único
    - NIT único
    - Database URL válida
    """
    repo = TenantRepository(session=session)
    
    # Validar nombre único
    if repo.get_by_name(name):
        raise ValueError(f"Tenant with name '{name}' already exists")
    
    # Validar NIT único
    if repo.get_by_nit(nit):
        raise ValueError(f"Tenant with NIT '{nit}' already exists")
    
    # Crear tenant
    tenant = Tenant(name=name, nit=nit, database_url=database_url, active=True)
    return repo.create(tenant)


def update_tenant(tenant_id: int, data: dict, session: Optional[Session] = None) -> Optional[Tenant]:
    """
    Actualiza tenant.
    
    Si se intenta cambiar nombre o NIT, valida que no estén duplicados.
    """
    repo = TenantRepository(session=session)
    
    # Validar nombre único si se cambia
    if "name" in data and data["name"]:
        existing = repo.get_by_name(data["name"])
        if existing and existing.id != tenant_id:
            raise ValueError(f"Tenant with name '{data['name']}' already exists")
    
    # Validar NIT único si se cambia
    if "nit" in data and data["nit"]:
        existing = repo.get_by_nit(data["nit"])
        if existing and existing.id != tenant_id:
            raise ValueError(f"Tenant with NIT '{data['nit']}' already exists")
    
    return repo.update(tenant_id, data)


def delete_tenant(tenant_id: int, session: Optional[Session] = None) -> bool:
    """Elimina tenant"""
    repo = TenantRepository(session=session)
    return repo.delete(tenant_id)
