from pydantic import BaseModel, EmailStr, constr, ConfigDict, Field
from typing import Optional
from enum import Enum


class Role(str, Enum):
    SYSTEM = "system"
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    username: constr(min_length=3, max_length=50)  # type: ignore
    password: constr(min_length=6)  # type: ignore
    email: Optional[EmailStr] = None
    role: Role = Role.USER
    zone_id: Optional[int] = None


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=6)] = None  # type: ignore
    role: Optional[Role] = None
    zone_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    tenant_id: int
    username: str
    email: Optional[EmailStr] = None
    role: Role
    is_active: bool
    zone_id: Optional[int] = None

