import os
import time
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.exc import OperationalError

# BD TENANT (la BD "productiva" del cliente)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
engine = create_engine(DATABASE_URL, echo=False)

# BD CENTRAL (almacena metadata de tenants)
CENTRAL_DATABASE_URL = os.getenv("CENTRAL_DATABASE_URL", "postgresql://appadmin:apppassword@db:5432/sanitation_central")
central_engine = create_engine(CENTRAL_DATABASE_URL, echo=False, pool_pre_ping=True)


def init_central_db(retries: int = 10, delay: int = 2):
    """Inicializa BD central con tabla de Tenant solamente"""
    from app.models.tenant import Tenant
    
    for attempt in range(1, retries + 1):
        try:
            # Crear SOLO la tabla Tenant (no todas las tablas)
            Tenant.__table__.create(central_engine, checkfirst=True)
            print("[Startup] Central database initialized")
            return
        except OperationalError as e:
            if attempt == retries:
                raise
            print(f"Central database not ready (attempt {attempt}/{retries}), retrying in {delay}s...")
            time.sleep(delay)


def init_db(retries: int = 10, delay: int = 2):
    """Inicializa BD del tenant con User, Company, Zone (NO incluye Tenant)"""
    from app.models.tenant import Tenant
    
    for attempt in range(1, retries + 1):
        try:
            # Crear todas las tablas EXCEPTO Tenant
            for table in SQLModel.metadata.sorted_tables:
                if table.name != 'tenant':  # Excluir tabla Tenant
                    table.create(engine, checkfirst=True)
            print("[Startup] Tenant database initialized")
            return
        except OperationalError as e:
            if attempt == retries:
                raise
            print(f"Database not ready (attempt {attempt}/{retries}), retrying in {delay}s...")
            time.sleep(delay)


def get_session():
    """Sesión para BD del tenant actual (usado en desarrollo)"""
    with Session(engine) as session:
        yield session
