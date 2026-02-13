
from datetime import timedelta
from typing import Optional
from sqlmodel import Session
from ..repositories.user_repository import UserRepository
from ..models.user import User, Role
from ..core.security import get_password_hash, verify_password, create_access_token
from ..db import engine


def register_user(
    username: str, 
    password: str, 
    tenant_id: int,
    session: Optional[Session] = None,
    email: Optional[str] = None, 
    role: Role = Role.USER
) -> User:
    """Registra usuario en la BD del tenant"""
    hashed = get_password_hash(password)
    user = User(
        username=username, 
        email=email, 
        hashed_password=hashed, 
        role=role,
        tenant_id=tenant_id
    )
    
    if session is None:
        repo = UserRepository()
        return repo.create(user)
    else:
        repo = UserRepository(session)
        return repo.create(user)


def authenticate_user(
    username: str, 
    password: str,
    tenant_id: int,
    session: Optional[Session] = None
) -> Optional[User]:
    """Autentica usuario contra su BD de tenant"""
    if session is None:
        repo = UserRepository()
    else:
        repo = UserRepository(session)
    
    user = repo.get_by_username(username, tenant_id)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user: User) -> str:
    """Crea JWT con user_id + tenant_id"""
    return create_access_token(subject=str(user.id), tenant_id=user.tenant_id)
