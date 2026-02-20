from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON, Index
from datetime import datetime


class AuditLog(SQLModel, table=True):
    """
    Audit log model - records ALL system actions for security and compliance.
    
    Tracks: Create, Update, Delete, Login, Execute formula, Export
    """
    __tablename__ = "audit_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Who performed the action
    user_id: int = Field(foreign_key="user.id", index=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    
    # What action was performed
    action: str = Field(index=True)  # "CREATE", "UPDATE", "DELETE", "LOGIN", "EXECUTE_FORMULA", "EXPORT"
    resource_type: str = Field(index=True)  # "User", "Zone", "Tariff", "Company", "Formula"
    resource_id: Optional[int] = Field(default=None, index=True)  # ID of affected resource
    
    # Old and new values (for auditing changes)
    old_values: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Technical metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Status of action
    status: str = Field(default="SUCCESS", index=True)  # "SUCCESS", "FAILURE", "UNAUTHORIZED"
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # When action occurred
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_company_timestamp', 'company_id', 'timestamp'),
        Index('idx_action_resource', 'action', 'resource_type'),
    )
