from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class Role(str, Enum):
    SYSTEM = "system"
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)  # Empresa a la que pertenece
    zone_id: Optional[int] = Field(default=None, foreign_key="zone.id")  # Zona opcional
    username: str = Field(index=True)  # Única por tenant, no global
    email: Optional[str] = None
    hashed_password: str
    is_active: bool = Field(default=True)
    role: Role = Field(default=Role.USER)
