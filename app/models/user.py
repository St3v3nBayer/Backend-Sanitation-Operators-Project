from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime
from pydantic import field_validator


class Role(str, Enum):
    SYSTEM = "system"
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    """
    User model refactored for single-tenant per company.
    
    - SYSTEM users: company_id MUST be NULL
    - ADMIN/USER: company_id MUST be set
    """
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Company relationship (NULL for SYSTEM, required for others)
    company_id: Optional[int] = Field(default=None, foreign_key="company.id", index=True)
    
    # User credentials
    username: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    hashed_password: str
    
    # Status
    is_active: bool = Field(default=True, index=True)
    role: Role = Field(default=Role.USER, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    @field_validator('company_id')
    @classmethod
    def validate_company_id(cls, v, info):
        """Validate company_id based on role"""
        role = info.data.get('role')
        if role == Role.SYSTEM and v is not None:
            raise ValueError("SYSTEM user cannot have a company_id")
        if role in [Role.ADMIN, Role.USER] and v is None:
            raise ValueError(f"{role} user must have a company_id")
        return v
