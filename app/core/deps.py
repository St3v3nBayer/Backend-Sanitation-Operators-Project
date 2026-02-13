from fastapi import Depends, HTTPException, Header
from sqlmodel import Session
from typing import Optional, Tuple
from ..core.security import decode_access_token
from ..repositories.user_repository import UserRepository
from ..db_manager import get_tenant_session
from ..models.user import User


def get_authorization_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return parts[1]


def get_current_user(token: str = Depends(get_authorization_token)) -> User:
    """Obtiene usuario de la BD con su tenant_id del JWT"""
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        tenant_id = int(payload.get("tenant_id"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session = get_tenant_session(tenant_id)
    user = UserRepository(session).get_by_id(user_id, tenant_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_with_tenant(
    token: str = Depends(get_authorization_token),
) -> Tuple[User, Session, int]:
    """
    Obtiene usuario + sesión de su tenant + tenant_id.
    
    Flujo:
    1. Decodifica JWT (contiene user_id + tenant_id)
    2. Obtiene sesión de BD del tenant
    3. Busca usuario en esa BD
    4. Retorna (user, session, tenant_id)
    
    Uso en rutas:
        @router.get("/")
        def list_items(user_data = Depends(get_current_user_with_tenant)):
            user, session, tenant_id = user_data
            # user existe en BD del tenant_id
    """
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        tenant_id = int(payload.get("tenant_id"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Obtener sesión de BD del tenant
    try:
        session = get_tenant_session(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    # Buscar usuario en BD del tenant
    user = UserRepository(session).get_by_id(user_id, tenant_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user, session, tenant_id
