from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from ..controllers.auth_controller import register_user, authenticate_user, create_token_for_user
from ..repositories.user_repository import UserRepository
from ..core.deps import get_current_user, get_current_user_with_tenant
from ..models.user import Role
from ..schemas.user import UserCreate as UserCreateSchema, UserRead
from ..db_manager import get_tenant_session
from ..db import central_engine
from ..models.tenant import Tenant

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/init", response_model=UserRead)
def init_system_user(payload: LoginRequest):
    """
    Initialize system user for default tenant (dev only, should be removed in production).
    Gets the default tenant from central DB and creates user in that tenant's DB.
    """
    # Obtener tenant por defecto
    with Session(central_engine) as central_session:
        tenant = central_session.exec(
            select(Tenant).where(Tenant.name == "default")
        ).first()
        
        if not tenant:
            raise HTTPException(status_code=500, detail="Default tenant not found")
    
    # Obtener sesión del tenant
    tenant_session = get_tenant_session(tenant.id)
    repo = UserRepository(tenant_session)
    
    existing = repo.get_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail=f"User {payload.username} already exists")
    
    user = register_user(
        payload.username, 
        payload.password, 
        tenant_id=tenant.id,
        session=tenant_session,
        email=None, 
        role=Role.SYSTEM
    )
    return UserRead.model_validate(user)


@router.post("/register", response_model=UserRead)
def register(payload: UserCreateSchema, user_data = Depends(get_current_user_with_tenant)):
    """
    Register new user in the current tenant's database.
    Only system or admin can register users; system can create admins.
    """
    current_user, tenant_session, tenant_id = user_data
    
    # Only system or admin can register users
    if current_user.role not in (Role.SYSTEM, Role.ADMIN):
        raise HTTPException(status_code=403, detail="Not authorized to register users")
    
    # Check if user already exists in this tenant
    repo = UserRepository(tenant_session)
    existing = repo.get_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered in this tenant")
    
    desired_role = Role(payload.role) if payload.role else Role.USER
    
    # Only system can create admins
    if desired_role == Role.ADMIN and current_user.role != Role.SYSTEM:
        raise HTTPException(status_code=403, detail="Only system role can create admin users")
    
    user = register_user(
        payload.username, 
        payload.password, 
        tenant_id=tenant_id,
        session=tenant_session,
        email=payload.email, 
        role=desired_role
    )
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(form_data: LoginRequest):
    """
    Login user.
    Returns token and user information.
    """
    # En desarrollo, intentar con el tenant por defecto
    with Session(central_engine) as central_session:
        tenant = central_session.exec(
            select(Tenant).where(Tenant.name == "default")
        ).first()
        
        if not tenant:
            raise HTTPException(status_code=500, detail="Default tenant not found")
    
    # Obtener sesión del tenant
    tenant_session = get_tenant_session(tenant.id)
    
    user = authenticate_user(form_data.username, form_data.password, tenant.id, session=tenant_session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token_for_user(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active,
        }
    }
