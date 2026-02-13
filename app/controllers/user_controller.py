from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash


def list_users(tenant_id: int, session=None) -> list[User]:
    """List all users for a tenant"""
    repo = UserRepository(session)
    return repo.get_all(tenant_id)


def get_user(user_id: int, tenant_id: int, session=None) -> User:
    """Get a user by ID with tenant isolation"""
    repo = UserRepository(session)
    user = repo.get_by_id(user_id, tenant_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user


def create_user(data: UserCreate, tenant_id: int, session=None) -> User:
    """Create a new user with validation"""
    repo = UserRepository(session)
    
    # Validate username is unique within tenant
    existing_user = repo.get_by_username(data.username, tenant_id)
    if existing_user:
        raise ValueError(f"Username '{data.username}' already exists in this tenant")
    
    # Validate email is unique within tenant if provided
    if data.email:
        existing_email = repo.get_by_email(data.email, tenant_id)
        if existing_email:
            raise ValueError(f"Email '{data.email}' already exists in this tenant")
    
    user = User(
        tenant_id=tenant_id,
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        zone_id=data.zone_id,
        is_active=True
    )
    return repo.create(user)


def update_user(user_id: int, tenant_id: int, data: UserUpdate, session=None) -> User:
    """Update an existing user"""
    repo = UserRepository(session)
    
    user = repo.get_by_id(user_id, tenant_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    # Update fields if provided
    if data.email is not None:
        # Validate email uniqueness if changed
        if data.email != user.email:
            existing = repo.get_by_email(data.email, tenant_id)
            if existing:
                raise ValueError(f"Email '{data.email}' already exists in this tenant")
        user.email = data.email
    
    if data.password is not None:
        user.hashed_password = get_password_hash(data.password)
    
    if data.role is not None:
        user.role = data.role
    
    if data.zone_id is not None:
        user.zone_id = data.zone_id
    
    if data.is_active is not None:
        user.is_active = data.is_active
    
    return repo.update(user)


def delete_user(user_id: int, tenant_id: int, session=None) -> bool:
    """Delete a user"""
    repo = UserRepository(session)
    
    user = repo.get_by_id(user_id, tenant_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    repo.delete(user)
    return True
