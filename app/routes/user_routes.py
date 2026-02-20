from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from ..schemas.user import UserCreate, UserUpdate, UserRead
from ..core.exceptions import (
    InsufficientPermissionsError,
    UserNotFoundError,
    UserCreationError,
    UserAccessDeniedError,
    DatabaseError,
)
from ..controllers.user_controller import (
    list_users,
    get_user,
    create_user,
    update_user,
    delete_user,
)
from ..core.deps import get_current_user, get_session, require_role
from ..models.user import User, Role
from ..repositories.audit_log_repository import AuditLogRepository

router = APIRouter()


@router.get("", response_model=list[UserRead])
def list_users_route(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List users
    - SYSTEM: sees all users globally
    - ADMIN: sees users from their company
    - USER: forbidden (403)
    """
    if user.role == Role.USER:
        raise InsufficientPermissionsError("Usuarios no pueden listar usuarios")
    
    try:
        if user.role == Role.SYSTEM:
            users = list_users(session=session)
        else:  # ADMIN
            users = list_users(session=session, company_id=user.company_id)
        
        return users
    except Exception as e:
        raise DatabaseError(str(e))


@router.get("/{user_id}", response_model=UserRead)
def get_user_route(
    user_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific user"""
    try:
        target_user = get_user(user_id, session=session)
        
        if not target_user:
            raise UserNotFoundError(user_id)
        
        # ADMIN can only see users from their company
        if user.role == Role.ADMIN and target_user.company_id != user.company_id:
            raise UserAccessDeniedError(user_id)
        
        return target_user
    except ValueError as e:
        raise UserNotFoundError(user_id)


@router.post("", response_model=UserRead, status_code=201)
def create_user_route(
    data: UserCreate,
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new user
    - SYSTEM: can create any role (admin, user)
    - ADMIN: can create USER role only in their company
    - USER: forbidden
    """
    if user.role not in [Role.SYSTEM, Role.ADMIN]:
        raise InsufficientPermissionsError("Solo SYSTEM y ADMIN pueden crear usuarios")
    
    try:
        # Enforce company context for ADMIN
        if user.role == Role.ADMIN:
            if data.company_id and data.company_id != user.company_id:
                raise InsufficientPermissionsError("No puedes crear usuarios fuera de tu empresa")
            data.company_id = user.company_id
            
            # ADMIN can only create USER role
            if data.role and data.role != Role.USER:
                raise InsufficientPermissionsError("Los ADMINs solo pueden crear usuarios con rol USER")
            data.role = Role.USER
        
        new_user = create_user(data, session=session)
        
        # Log the action
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=user.company_id or new_user.company_id,
            action="CREATE",
            resource_type="User",
            resource_id=new_user.id,
            new_values={
                "username": new_user.username,
                "role": new_user.role.value,
                "company_id": new_user.company_id
            },
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
        
        return new_user
    
    except ValueError as e:
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=user.company_id,
            action="CREATE",
            resource_type="User",
            status="FAILURE",
            status_code=400,
            error_message=str(e),
            ip_address=request.client.host if request.client else None,
        )
        raise UserCreationError(str(e))


@router.put("/{user_id}", response_model=UserRead)
def update_user_route(
    user_id: int,
    data: UserUpdate,
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Update a user
    - SYSTEM: can update any user
    - ADMIN: can update users in their company (no role changes)
    - USER: can only update themselves (email, password)
    """
    try:
        target_user = get_user(user_id, session=session)
        if not target_user:
            raise UserNotFoundError(user_id)
        
        # Permission checks
        if user.role == Role.USER:
            if user_id != user.id:
                raise UserAccessDeniedError(user_id)
        elif user.role == Role.ADMIN:
            if target_user.company_id != user.company_id:
                raise UserAccessDeniedError(user_id)
            if data.role:
                raise InsufficientPermissionsError("Los ADMINs no pueden cambiar roles de usuarios")
        
        # Store old values for audit
        old_values = {
            "email": target_user.email,
            "role": target_user.role.value,
            "is_active": target_user.is_active,
        }
        
        updated_user = update_user(user_id, data, session=session)
        
        # Log the action
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=user.company_id,
            action="UPDATE",
            resource_type="User",
            resource_id=updated_user.id,
            old_values=old_values,
            new_values={
                "email": updated_user.email,
                "role": updated_user.role.value,
                "is_active": updated_user.is_active,
            },
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
        
        return updated_user
    except ValueError as e:
        raise UserCreationError(str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user_route(
    user_id: int,
    request: Request,
    user: User = Depends(require_role(Role.SYSTEM)),  # Only SYSTEM can delete
    session: Session = Depends(get_session),
):
    """Delete a user (SYSTEM only)"""
    try:
        target_user = get_user(user_id, session=session)
        if not target_user:
            raise UserNotFoundError(user_id)
        
        delete_user(user_id, session=session)
        
        # Log the action
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=user.company_id or target_user.company_id,
            action="DELETE",
            resource_type="User",
            resource_id=user_id,
            old_values={
                "username": target_user.username,
                "role": target_user.role.value,
            },
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
    except ValueError as e:
        raise UserNotFoundError(user_id)
