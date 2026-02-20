from pydantic import BaseModel, EmailStr, constr, ConfigDict, Field, field_validator
from typing import Optional
from enum import Enum
from datetime import datetime


class Role(str, Enum):
    SYSTEM = "system"
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    model_config = ConfigDict(extra="forbid")
    
    username: constr(min_length=3, max_length=50)  # type: ignore
    password: constr(min_length=8)  # type: ignore - stronger password requirement
    email: Optional[EmailStr] = None
    role: Role = Role.USER
    company_id: Optional[int] = None  # Required for ADMIN/USER, NULL for SYSTEM
    
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


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    model_config = ConfigDict(extra="forbid")
    
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None  # type: ignore
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    # NOTE: company_id is immutable and cannot be changed


class UserRead(BaseModel):
    """Schema for returning user data in responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    company_id: Optional[int]  # NULL for SYSTEM users
    username: str
    email: Optional[EmailStr] = None
    role: Role
    is_active: bool = Field(serialization_alias='active')  # Renamed to 'active' in JSON response
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

