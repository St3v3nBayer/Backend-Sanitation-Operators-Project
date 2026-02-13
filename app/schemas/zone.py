from sqlmodel import SQLModel
from pydantic import ConfigDict
from typing import Optional


class ZoneCreate(SQLModel):
    """Esquema para crear una zona"""
    name: str
    active_users: int = 0


class ZoneUpdate(SQLModel):
    """Esquema para actualizar una zona"""
    name: Optional[str] = None
    active_users: Optional[int] = None
    active: Optional[bool] = None


class ZoneRead(SQLModel):
    """Esquema para leer una zona (respuesta del API)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    tenant_id: int
    name: str
    active_users: int
    active: bool
