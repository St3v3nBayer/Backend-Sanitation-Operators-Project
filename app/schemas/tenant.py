from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TenantCreate(BaseModel):
    """Schema para crear nuevo tenant"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., min_length=3, max_length=100)
    nit: str = Field(..., min_length=5, max_length=20)
    database_url: str = Field(..., description="PostgreSQL connection string")


class TenantUpdate(BaseModel):
    """Schema para actualizar tenant"""
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    nit: Optional[str] = Field(None, min_length=5, max_length=20)
    database_url: Optional[str] = None
    active: Optional[bool] = None


class TenantRead(BaseModel):
    """Schema para respuesta de tenant (sin exponer datos sensibles)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    nit: str
    active: bool
    created_at: datetime
    updated_at: datetime
