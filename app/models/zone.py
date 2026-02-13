from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict
from typing import Optional


class Zone(SQLModel, table=True):
    """Representa una zona dentro de una empresa (ej: Bogotá, Quindío)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(primary_key=True)
    tenant_id: int  # FK a Tenant para multi-tenancy
    name: str  # "Bogotá", "Quindío"
    active_users: int = Field(default=0)  # Cantidad de usuarios activos
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
