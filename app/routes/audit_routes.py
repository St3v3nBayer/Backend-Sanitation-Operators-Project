from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session
from datetime import datetime
from typing import Optional

from ..core.deps import get_current_user, require_system_user, require_company_access
from ..db import get_session
from ..models.user import User, Role
from ..schemas.audit_log import AuditLogRead, AuditLogListResponse
from ..repositories.audit_log_repository import AuditLogRepository
from ..core.exceptions import (
    AuditLogAccessDeniedError,
    AuditLogNotFoundError,
    NotImplementedFeatureError,
)

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
def list_audit_logs(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    days: int = Query(30, ge=1, le=365),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    user_filter: Optional[int] = Query(None),
) -> AuditLogListResponse:
    """
    List audit logs for the current user's company.
    
    - SYSTEM: Can see logs from all companies (not implemented yet)
    - ADMIN: Can see logs from their company
    - USER: Cannot access (403)
    """
    if user.role == Role.USER:
        raise AuditLogAccessDeniedError()
    
    audit_repo = AuditLogRepository(session)
    
    # Get company_id (SYSTEM users may need special handling)
    if user.role == Role.SYSTEM:
        # TODO: Implement multi-company retrieval for SYSTEM users
        raise NotImplementedFeatureError("Obtención de registros de auditoría para SYSTEM")
    
    # ADMIN - get their company only
    company_id = user.company_id
    
    logs = audit_repo.get_logs(
        company_id=company_id,
        days=days,
        action=action,
        resource_type=resource_type,
        user_id=user_filter,
    )
    
    return AuditLogListResponse(
        total=len(logs),
        logs=[AuditLogRead.from_orm(log) for log in logs],
    )


@router.get("/logs/{log_id}")
def get_audit_log(
    log_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AuditLogRead:
    """Get specific audit log entry"""
    if user.role == Role.USER:
        raise AuditLogAccessDeniedError()
    
    audit_repo = AuditLogRepository(session)
    log = audit_repo.get_by_id(log_id)
    
    if not log:
        raise AuditLogNotFoundError(log_id)
    
    # Verify company access
    if user.role == Role.ADMIN and log.company_id != user.company_id:
        raise AuditLogAccessDeniedError()
    
    return AuditLogRead.from_orm(log)


@router.get("/user-activity")
def get_user_recent_activity(
    user_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
) -> list[AuditLogRead]:
    """
    Get recent activity for a user.
    
    - SYSTEM: Can see activity of any user
    - ADMIN: Can see activity of users in their company
    - USER: Can only see their own activity
    """
    if user_id is None:
        user_id = user.id
    
    # Verify permissions
    if user.role == Role.USER and user_id != user.id:
        raise AuditLogAccessDeniedError()
    
    audit_repo = AuditLogRepository(session)
    activity = audit_repo.get_user_activity(user_id=user_id, limit=limit)
    
    return [AuditLogRead.from_orm(log) for log in activity]


@router.get("/resource-history")
def get_resource_history(
    resource_type: str,
    resource_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[AuditLogRead]:
    """
    Get all changes made to a specific resource.
    
    Requires appropriate company access.
    """
    if user.role == Role.USER:
        raise AuditLogAccessDeniedError()
    
    audit_repo = AuditLogRepository(session)
    
    # Get company context
    company_id = user.company_id
    if not company_id and user.role != Role.SYSTEM:
        raise AuditLogAccessDeniedError()
    
    history = audit_repo.get_resource_history(
        company_id=company_id,
        resource_type=resource_type,
        resource_id=resource_id
    )
    
    return [AuditLogRead.from_orm(log) for log in history]
