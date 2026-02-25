from pydantic import BaseModel, EmailStr, constr, ConfigDict
from typing import Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: constr(min_length=1)
    nit: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class CompanyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[constr(min_length=1)] = None
    nit: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    nit: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
