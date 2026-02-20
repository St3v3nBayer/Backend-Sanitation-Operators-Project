from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class AuditLogRead(BaseModel):
    """Schema for returning audit log data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    company_id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    status: str
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs"""
    action: Optional[str] = None
    resource_type: Optional[str] = None
    user_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None


class AuditLogListResponse(BaseModel):
    """Response for listing audit logs"""
    total: int
    logs: List[AuditLogRead]
    filters: Optional[AuditLogFilter] = None


class AuditLogExport(BaseModel):
    """Response for exporting audit logs"""
    filename: str
    rows_count: int
    generated_at: datetime
