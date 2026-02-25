from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from .db import init_db, engine
from .core.error_handler import register_exception_handlers
from .repositories.user_repository import UserRepository
from .repositories.company_repository import CompanyRepository
from .controllers.auth_controller import register_user
from .models.user import Role, User
from .models.company import Company
# Import all models for SQLModel metadata
from .models.audit_log import AuditLog
from .models.aps import APS
from .models.aps_monthly_data import APSMonthlyData
from .models.tariff_calculation import TariffCalculation
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle - startup and shutdown"""
    try:
        # 1. Initialize database
        init_db()
        print("[Startup] Database initialized")
        
        # 2. Seed default company if needed
        with Session(engine) as session:
            company_repo = CompanyRepository(session)
            default_company = company_repo.get_by_name("Default Company")
            
            if not default_company:
                default_company = Company(
                    name="Default Company",
                    nit="0000000000",
                    email="admin@default.com"
                )
                default_company = company_repo.create(default_company)
                print("[Startup] Created default company")
                default_company_id = default_company.id
            else:
                default_company_id = default_company.id
        
        # 3. Create SYSTEM admin user if specified in env vars
        admin_user = os.getenv("ADMIN_USERNAME", "admin")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin123456")
        
        if admin_user and admin_pass:
            with Session(engine) as session:
                user_repo = UserRepository(session)
                
                if not user_repo.get_by_username(admin_user):
                    user = register_user(
                        username=admin_user,
                        password=admin_pass,
                        session=session,
                        email="admin@system.com",
                        role=Role.SYSTEM,
                        company_id=None,  # SYSTEM users have no company
                    )
                    print(f"[Startup] Created SYSTEM user: {admin_user}")
                else:
                    print(f"[Startup] Admin user {admin_user} already exists")
        
        print("[Startup] Application ready")
    except Exception as e:
        print(f"[Startup] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    # Shutdown logic
    print("[Shutdown] Application closing")


app = FastAPI(
    title="Sanitation Operators API",
    description="API for managing sanitation companies, tariffs, and users",
    version="2.0.0",
    lifespan=lifespan
)

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

# Register exception handlers
register_exception_handlers(app)

# Include routers
from .routes.auth_routes import router as auth_router
from .routes.company_routes import router as company_router
from .routes.user_routes import router as user_router
from .routes.audit_routes import router as audit_router
from .routes.aps import router as aps_router
from .routes.tariff_calculation import router as tariff_calc_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(company_router, prefix="/companies", tags=["companies"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])
app.include_router(aps_router, prefix="/api")
app.include_router(tariff_calc_router, prefix="/api")

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "mode": "single-tenant"
    }