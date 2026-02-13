from ..models.zone import Zone
from ..repositories.zone_repository import ZoneRepository
from ..schemas.zone import ZoneCreate, ZoneUpdate


def list_zones(tenant_id: int, session=None) -> list[Zone]:
    """Lista todas las zonas del tenant"""
    repo = ZoneRepository(session)
    return repo.get_all(tenant_id)


def get_zone(zone_id: int, tenant_id: int, session=None) -> Zone:
    """Obtiene una zona por ID"""
    repo = ZoneRepository(session)
    zone = repo.get_by_id(zone_id, tenant_id)
    if not zone:
        raise ValueError(f"Zone {zone_id} not found")
    return zone


def create_zone(name: str, active_users: int, tenant_id: int, session=None) -> Zone:
    """Crea una nueva zona con validación de nombre único"""
    repo = ZoneRepository(session)
    
    # Validar que el nombre sea único en el tenant
    existing = repo.get_by_name(name, tenant_id)
    if existing:
        raise ValueError(f"Zone with name '{name}' already exists in this tenant")
    
    zone = Zone(
        name=name,
        active_users=active_users,
        tenant_id=tenant_id,
        active=True
    )
    return repo.create(zone)


def update_zone(zone_id: int, tenant_id: int, data: dict, session=None) -> Zone:
    """Actualiza una zona existente"""
    repo = ZoneRepository(session)
    
    # Si se actualiza el nombre, validar unicidad
    if "name" in data and data["name"]:
        existing = repo.get_by_name(data["name"], tenant_id)
        if existing and existing.id != zone_id:
            raise ValueError(f"Zone with name '{data['name']}' already exists")
    
    updated = repo.update(zone_id, tenant_id, data)
    if not updated:
        raise ValueError(f"Zone {zone_id} not found")
    return updated


def delete_zone(zone_id: int, tenant_id: int, session=None) -> bool:
    """Elimina una zona"""
    repo = ZoneRepository(session)
    if not repo.delete(zone_id, tenant_id):
        raise ValueError(f"Zone {zone_id} not found")
    return True
