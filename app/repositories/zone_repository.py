from sqlmodel import Session, select
from ..models.zone import Zone


class ZoneRepository:
    """Repositorio para operaciones CRUD de zonas en la BD del tenant"""

    def __init__(self, session: Session | None = None):
        self.session = session

    def get_all(self, tenant_id: int) -> list[Zone]:
        """Obtiene todas las zonas del tenant"""
        return self.session.exec(
            select(Zone).where(Zone.tenant_id == tenant_id)
        ).all()

    def get_by_id(self, zone_id: int, tenant_id: int) -> Zone | None:
        """Obtiene una zona por ID (con validación de tenant)"""
        return self.session.exec(
            select(Zone).where(
                Zone.id == zone_id,
                Zone.tenant_id == tenant_id
            )
        ).first()

    def get_by_name(self, name: str, tenant_id: int) -> Zone | None:
        """Obtiene una zona por nombre (con validación de tenant)"""
        return self.session.exec(
            select(Zone).where(
                Zone.name == name,
                Zone.tenant_id == tenant_id
            )
        ).first()

    def create(self, zone: Zone) -> Zone:
        """Crea una nueva zona"""
        self.session.add(zone)
        self.session.commit()
        self.session.refresh(zone)
        return zone

    def update(self, zone_id: int, tenant_id: int, updates: dict) -> Zone | None:
        """Actualiza una zona existente"""
        zone = self.get_by_id(zone_id, tenant_id)
        if not zone:
            return None

        for key, value in updates.items():
            if value is not None:
                setattr(zone, key, value)

        self.session.add(zone)
        self.session.commit()
        self.session.refresh(zone)
        return zone

    def delete(self, zone_id: int, tenant_id: int) -> bool:
        """Elimina una zona"""
        zone = self.get_by_id(zone_id, tenant_id)
        if not zone:
            return False

        self.session.delete(zone)
        self.session.commit()
        return True
