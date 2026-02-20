
from datetime import timedelta
from typing import Optional
from sqlmodel import Session
from ..repositories.user_repository import UserRepository
from ..models.user import User, Role
from ..core.security import get_password_hash, verify_password, create_access_token


def register_user(
    username: str,
    password: str,
    session: Session,
    email: Optional[str] = None,
    role: Role = Role.USER,
    company_id: Optional[int] = None,
) -> User:
    """Register a new user"""
    hashed = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        role=role,
        company_id=company_id,
        is_active=True,
    )
    
    repo = UserRepository(session)
    return repo.create(user)


def authenticate_user(
    username: str,
    password: str,
    session: Session,
) -> Optional[User]:
    """Authenticate user and return user object if successful"""
    repo = UserRepository(session)
    
    user = repo.get_by_username(username)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_token_for_user(user: User) -> str:
    """Create JWT access token for user"""
    return create_access_token(
        subject=str(user.id),
        company_id=user.company_id,
        role=user.role.value,
    )
