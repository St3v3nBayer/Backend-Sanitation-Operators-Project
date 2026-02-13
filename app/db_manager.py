import os
from sqlmodel import Session, create_engine, select
from sqlalchemy.pool import NullPool
from app.models.tenant import Tenant

# BD CENTRAL (almacena metadata de tenants)
CENTRAL_DATABASE_URL = os.getenv("CENTRAL_DATABASE_URL", "postgresql://appadmin:apppassword@db:5432/sanitation_central")

central_engine = create_engine(
    CENTRAL_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


def get_tenant_by_id(tenant_id: int) -> Tenant:
    """Obtiene configuración del tenant desde BD central"""
    with Session(central_engine) as session:
        tenant = session.exec(
            select(Tenant).where(Tenant.id == tenant_id)
        ).first()
        
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        if not tenant.active:
            raise ValueError(f"Tenant {tenant_id} is inactive")
        
        return tenant


def get_tenant_engine(database_url: str):
    """Crea un engine dinámico para un tenant específico"""
    return create_engine(
        database_url,
        poolclass=NullPool,  # No mantener conexiones entre requests
        echo=False,
    )


def get_tenant_session(tenant_id: int) -> Session:
    """
    Obtiene una sesión de BD del tenant correcto.
    
    Flujo:
    1. Busca en BD central la config del tenant
    2. Crea engine dinámico para esa BD
    3. Retorna sesión lista para usar
    """
    tenant = get_tenant_by_id(tenant_id)
    engine = get_tenant_engine(tenant.database_url)
    return Session(engine)
