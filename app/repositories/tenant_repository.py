from typing import List, Optional
from sqlmodel import Session, select
from ..models.tenant import Tenant
from ..db import central_engine


class TenantRepository:
    """Repositorio para gestionar Tenants en BD central"""
    
    def __init__(self, session: Optional[Session] = None):
        """Inicializa repository con sesión opcional"""
        self._session = session
        self._owns_session = session is None
        if session is None:
            self._session = Session(central_engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session:
            self._session.close()

    def get_all(self) -> List[Tenant]:
        """Obtiene todos los tenants"""
        return self._session.exec(select(Tenant)).all()

    def get_by_id(self, tenant_id: int) -> Optional[Tenant]:
        """Obtiene tenant por ID"""
        return self._session.get(Tenant, tenant_id)

    def get_by_name(self, name: str) -> Optional[Tenant]:
        """Obtiene tenant por nombre"""
        return self._session.exec(
            select(Tenant).where(Tenant.name == name)
        ).first()

    def get_by_nit(self, nit: str) -> Optional[Tenant]:
        """Obtiene tenant por NIT"""
        return self._session.exec(
            select(Tenant).where(Tenant.nit == nit)
        ).first()

    def create(self, tenant: Tenant) -> Tenant:
        """Crea nuevo tenant"""
        self._session.add(tenant)
        self._session.commit()
        self._session.refresh(tenant)
        return tenant

    def update(self, tenant_id: int, data: dict) -> Optional[Tenant]:
        """Actualiza tenant"""
        tenant = self._session.get(Tenant, tenant_id)
        if not tenant:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(tenant, key, value)
        self._session.add(tenant)
        self._session.commit()
        self._session.refresh(tenant)
        return tenant

    def delete(self, tenant_id: int) -> bool:
        """Elimina tenant"""
        tenant = self._session.get(Tenant, tenant_id)
        if not tenant:
            return False
        self._session.delete(tenant)
        self._session.commit()
        return True
