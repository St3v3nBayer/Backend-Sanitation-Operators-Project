from fastapi import Depends, HTTPException, Header, Request
from sqlmodel import Session
from typing import Optional
from ..core.security import decode_access_token
from ..repositories.user_repository import UserRepository
from ..db import get_session
from ..models.user import User, Role


def get_authorization_token(request: Request) -> str:
    """Extract bearer token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    return parts[1]


def get_current_user(
    token: str = Depends(get_authorization_token),
    session: Session = Depends(get_session),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    In single-tenant mode:
    - Decode JWT (contains user_id, company_id, role)
    - Fetch user from local database
    - Validate user is active
    """
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from local database
    repo = UserRepository(session)
    user = repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    
    return user


def require_role(*required_roles: Role):
    """
    Decorator factory to require specific roles.
    
    Usage:
        @router.post("/admin/users")
        def create_user(user: User = Depends(require_role(Role.ADMIN, Role.SYSTEM))):
            ...
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"This action requires one of these roles: {[r.value for r in required_roles]}"
            )
        return user
    return role_checker


def require_system_user(user: User = Depends(get_current_user)) -> User:
    """Require SYSTEM role"""
    if user.role != Role.SYSTEM:
        raise HTTPException(status_code=403, detail="This action is only available to SYSTEM users")
    return user


def require_company_access(user: User = Depends(get_current_user)) -> User:
    """Require user has company assigned (not SYSTEM)"""
    if user.company_id is None:
        raise HTTPException(status_code=403, detail="This action requires a company assignment")
    return user

def check_user_role(user: User, allowed_roles: list):
    """
    Helper function to check if user has one of the allowed roles.
    
    Args:
        user: User object
        allowed_roles: List of role strings like ["SYSTEM", "ADMIN"]
    
    Raises:
        HTTPException if user doesn't have required role
    """
    # Convert string roles to Role enum
    role_enums = []
    for role in allowed_roles:
        if isinstance(role, str):
            try:
                role_enums.append(Role[role])
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        else:
            role_enums.append(role)
    
    if user.role not in role_enums:
        raise HTTPException(
            status_code=403,
            detail=f"This action requires one of these roles: {allowed_roles}"
        )
    return True