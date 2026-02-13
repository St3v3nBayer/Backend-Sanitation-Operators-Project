from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from .db import init_db, init_central_db, central_engine, engine
from .db_manager import get_tenant_session
from .routes.company_routes import router as company_router
from .routes.auth_routes import router as auth_router
from .routes.user_routes import router as user_router
from .repositories.user_repository import UserRepository
from .controllers.auth_controller import register_user
from .models.user import Role
# Importar TODOS los modelos para que estén en el metadata
from .models.tenant import Tenant
from .models.zone import Zone
from .models.user import User
from .models.company import Company
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        # 1. Inicializar BD central
        init_central_db()
        
        # 2. Crear tenant por defecto si no existe (para desarrollo)
        with Session(central_engine) as session:
            default_tenant = session.exec(
                select(Tenant).where(Tenant.name == "default")
            ).first()
            
            if not default_tenant:
                # Crear tenant por defecto apuntando a la BD actual
                tenant = Tenant(
                    name="default",
                    nit="000000000",
                    database_url=os.getenv("DATABASE_URL", "sqlite:///./dev.db"),
                    active=True
                )
                session.add(tenant)
                session.commit()
                session.refresh(tenant)
                print("[Startup] Created default tenant")
                default_tenant_id = tenant.id
            else:
                default_tenant_id = default_tenant.id
        
        # 3. Inicializar BD del tenant (la BD del cliente)
        init_db()
        
        # 4. Crear usuario admin si se especifica en variables de entorno
        # Default para desarrollo: systemuser / system1234
        admin_user = os.getenv("ADMIN_USERNAME", "systemuser")
        admin_pass = os.getenv("ADMIN_PASSWORD", "system1234")
        admin_role_str = os.getenv("ADMIN_ROLE", "system")
        
        if admin_user and admin_pass:
            try:
                admin_role = Role(admin_role_str)
            except Exception:
                admin_role = Role.SYSTEM
            
            # Obtener sesión del tenant por defecto
            tenant_session = get_tenant_session(default_tenant_id)
            repo = UserRepository(tenant_session)
            
            if not repo.get_by_username(admin_user, default_tenant_id):
                user = register_user(
                    admin_user, 
                    admin_pass, 
                    tenant_id=default_tenant_id,
                    session=tenant_session,
                    email=None, 
                    role=admin_role
                )
                print(f"[Startup] Created initial admin user: {admin_user} with role {admin_role}")
            else:
                print(f"[Startup] Admin user {admin_user} already exists")
        else:
            print("[Startup] ADMIN_USERNAME or ADMIN_PASSWORD not set, skipping seed")
            
    except Exception as e:
        print(f"[Startup] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    yield
    # Shutdown logic (if needed)


app = FastAPI(title="Sanitation Operators API", lifespan=lifespan)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(company_router, prefix="/companies", tags=["companies"])
app.include_router(user_router, prefix="/users", tags=["users"])

# Zone router - import here to avoid circular imports
from .routes.zone_routes import router as zone_router
app.include_router(zone_router, prefix="/zones", tags=["zones"])

# Admin router - import here to avoid circular imports
from .routes.admin_routes import router as admin_router
app.include_router(admin_router, prefix="/admin", tags=["admin"])