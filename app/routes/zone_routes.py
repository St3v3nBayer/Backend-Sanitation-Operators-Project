from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from ..schemas.zone import ZoneCreate, ZoneUpdate, ZoneRead
from ..controllers.zone_controller import (
    list_zones,
    get_zone,
    create_zone,
    update_zone,
    delete_zone,
)
from ..core.deps import get_current_user_with_tenant

router = APIRouter()


@router.get("", response_model=list[ZoneRead])
def list_zones_endpoint(user_data = Depends(get_current_user_with_tenant)):
    """Lista todas las zonas del tenant del usuario actual"""
    user, session, tenant_id = user_data
    try:
        zones = list_zones(tenant_id, session=session)
        return zones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{zone_id}", response_model=ZoneRead)
def get_zone_endpoint(zone_id: int, user_data = Depends(get_current_user_with_tenant)):
    """Obtiene una zona específica"""
    user, session, tenant_id = user_data
    try:
        zone = get_zone(zone_id, tenant_id, session=session)
        return zone
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=ZoneRead, status_code=201)
def create_zone_endpoint(
    data: ZoneCreate,
    user_data = Depends(get_current_user_with_tenant)
):
    """Crea una nueva zona en el tenant actual"""
    user, session, tenant_id = user_data
    try:
        zone = create_zone(
            name=data.name,
            active_users=data.active_users,
            tenant_id=tenant_id,
            session=session
        )
        return zone
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{zone_id}", response_model=ZoneRead)
def update_zone_endpoint(
    zone_id: int,
    data: ZoneUpdate,
    user_data = Depends(get_current_user_with_tenant)
):
    """Actualiza una zona existente"""
    user, session, tenant_id = user_data
    try:
        update_data = data.model_dump(exclude_unset=True)
        zone = update_zone(zone_id, tenant_id, update_data, session=session)
        return zone
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{zone_id}", status_code=204)
def delete_zone_endpoint(
    zone_id: int,
    user_data = Depends(get_current_user_with_tenant)
):
    """Elimina una zona"""
    user, session, tenant_id = user_data
    try:
        delete_zone(zone_id, tenant_id, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
