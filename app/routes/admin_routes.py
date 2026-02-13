from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..core.deps import get_current_user
from ..models.user import Role, User
from ..schemas.tenant import TenantCreate, TenantUpdate, TenantRead
from ..controllers.admin_controller import (
    list_tenants,
    get_tenant,
    create_tenant,
    update_tenant,
    delete_tenant,
)

router = APIRouter()


def check_system_role(current_user: User = Depends(get_current_user)) -> User:
    """Valida que el usuario tenga rol SYSTEM"""
    if current_user.role != Role.SYSTEM:
        raise HTTPException(
            status_code=403,
            detail="Only SYSTEM role can access admin endpoints"
        )
    return current_user


@router.get("/tenants", response_model=List[TenantRead])
def list_tenants_endpoint(current_user: User = Depends(check_system_role)):
    """Lista todos los tenants (solo SYSTEM)"""
    tenants = list_tenants()
    return [TenantRead.model_validate(t) for t in tenants]


@router.get("/tenants/{tenant_id}", response_model=TenantRead)
def get_tenant_endpoint(tenant_id: int, current_user: User = Depends(check_system_role)):
    """Obtiene tenant por ID (solo SYSTEM)"""
    tenant = get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantRead.model_validate(tenant)


@router.post("/tenants", response_model=TenantRead, status_code=201)
def create_tenant_endpoint(
    payload: TenantCreate,
    current_user: User = Depends(check_system_role)
):
    """Crea nuevo tenant (solo SYSTEM)"""
    try:
        tenant = create_tenant(
            name=payload.name,
            nit=payload.nit,
            database_url=payload.database_url
        )
        return TenantRead.model_validate(tenant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/tenants/{tenant_id}", response_model=TenantRead)
def update_tenant_endpoint(
    tenant_id: int,
    payload: TenantUpdate,
    current_user: User = Depends(check_system_role)
):
    """Actualiza tenant (solo SYSTEM)"""
    try:
        tenant = update_tenant(tenant_id, payload.model_dump(exclude_unset=True))
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return TenantRead.model_validate(tenant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tenants/{tenant_id}", status_code=204)
def delete_tenant_endpoint(
    tenant_id: int,
    current_user: User = Depends(check_system_role)
):
    """Elimina tenant (solo SYSTEM)"""
    ok = delete_tenant(tenant_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return None
