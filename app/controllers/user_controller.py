from typing import Optional, List
from sqlmodel import Session
from ..models.user import User, Role
from ..models.company import Company
from ..schemas.user import UserCreate, UserUpdate
from ..repositories.user_repository import UserRepository
from ..repositories.company_repository import CompanyRepository
from ..core.security import get_password_hash


def list_users(
    session: Session,
    company_id: Optional[int] = None,
    role: Optional[Role] = None,
) -> List[User]:
    """List users with optional filters"""
    repo = UserRepository(session)
    users = repo.get_all(role_filter=role)
    
    if company_id:
        users = [u for u in users if u.company_id == company_id]
    
    return users


def get_user(user_id: int, session: Session) -> Optional[User]:
    """Get a user by ID"""
    repo = UserRepository(session)
    return repo.get_by_id(user_id)


def create_user(data: UserCreate, session: Session) -> User:
    """
    Create a new user with validation.
    
    - Validates username uniqueness
    - Validates company exists (if required)
    - Validates role + company_id relationship
    """
    repo = UserRepository(session)
    company_repo = CompanyRepository(session)
    
    # Validate username is unique
    if repo.get_by_username(data.username):
        raise ValueError(f"Username '{data.username}' already exists")
    
    # Validate email is unique (if provided)
    if data.email and repo.get_by_email(data.email):
        raise ValueError(f"Email '{data.email}' already exists")
    
    # Validate company exists (if required)
    if data.company_id:
        if not company_repo.get_by_id(data.company_id):
            raise ValueError(f"Company {data.company_id} does not exist")
    
    # Validate role + company_id relationship
    if data.role == Role.SYSTEM and data.company_id:
        raise ValueError("SYSTEM user cannot have a company_id")
    if data.role != Role.SYSTEM and not data.company_id:
        raise ValueError(f"{data.role} user must have a company_id")
    
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        company_id=data.company_id,
        is_active=True,
    )
    
    return repo.create(user)


def update_user(user_id: int, data: UserUpdate, session: Session) -> User:
    """Update a user (cannot change company_id)"""
    repo = UserRepository(session)
    company_repo = CompanyRepository(session)
    
    user = repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    # Update email
    if data.email is not None:
        if data.email != user.email:
            if repo.get_by_email(data.email):
                raise ValueError(f"Email '{data.email}' already exists")
        user.email = data.email
    
    # Update password
    if data.password is not None:
        user.hashed_password = get_password_hash(data.password)
    
    # Update role (with validation for company_id)
    if data.role is not None:
        if data.role == Role.SYSTEM and user.company_id:
            raise ValueError("Cannot change to SYSTEM role with company assigned")
        user.role = data.role
    
    # Update is_active
    if data.is_active is not None:
        user.is_active = data.is_active
    
    return repo.update(user)


def delete_user(user_id: int, session: Session) -> bool:
    """Delete a user (only SYSTEM role can delete)"""
    repo = UserRepository(session)
    
    user = repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    repo.delete(user)
    return True
