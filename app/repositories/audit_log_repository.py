from typing import Optional, List
from sqlmodel import Session, select, desc
from datetime import datetime, timedelta
from ..models.audit_log import AuditLog


class AuditLogRepository:
    """Data access layer for AuditLog model"""
    
    def __init__(self, session: Session):
        """Initialize repository with session."""
        self.session = session

    def log_action(
        self,
        user_id: int,
        company_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS",
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an action to audit trail
        
        Args:
            user_id: ID of user performing action
            company_id: ID of company affected
            action: Action type (CREATE, UPDATE, DELETE, LOGIN, EXECUTE_FORMULA, EXPORT)
            resource_type: Type of resource (User, Zone, Tariff, Company, Formula)
            resource_id: ID of resource affected
            old_values: Previous values (for UPDATE)
            new_values: New values
            ip_address: Client IP address
            user_agent: Client user agent
            status: Status of action (SUCCESS, FAILURE, UNAUTHORIZED)
            status_code: HTTP status code
            error_message: Error message if failed
        """
        audit = AuditLog(
            user_id=user_id,
            company_id=company_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            status_code=status_code,
            error_message=error_message,
        )
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        return audit

    def get_logs(
        self,
        company_id: int,
        days: int = 30,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> List[AuditLog]:
        """
        Get audit logs for a company
        
        Args:
            company_id: Company ID
            days: Number of days to look back
            action: Filter by action type
            resource_type: Filter by resource type
            user_id: Filter by user ID
        """
        date_from = datetime.utcnow() - timedelta(days=days)
        
        statement = select(AuditLog).where(
            (AuditLog.company_id == company_id) &
            (AuditLog.timestamp >= date_from)
        )
        
        if action:
            statement = statement.where(AuditLog.action == action)
        if resource_type:
            statement = statement.where(AuditLog.resource_type == resource_type)
        if user_id:
            statement = statement.where(AuditLog.user_id == user_id)
        
        return self.session.exec(
            statement.order_by(desc(AuditLog.timestamp))
        ).all()

    def get_user_activity(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[AuditLog]:
        """Get latest actions performed by a user"""
        return self.session.exec(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
        ).all()

    def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        """Get specific audit log entry"""
        return self.session.exec(
            select(AuditLog).where(AuditLog.id == log_id)
        ).first()

    def get_resource_history(
        self,
        company_id: int,
        resource_type: str,
        resource_id: int,
    ) -> List[AuditLog]:
        """Get all changes made to a specific resource"""
        return self.session.exec(
            select(AuditLog).where(
                (AuditLog.company_id == company_id) &
                (AuditLog.resource_type == resource_type) &
                (AuditLog.resource_id == resource_id)
            ).order_by(AuditLog.timestamp)
        ).all()
