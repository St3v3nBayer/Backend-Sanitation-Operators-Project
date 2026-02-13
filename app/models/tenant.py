from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict
from typing import Optional


class Tenant(SQLModel, table=True):
    """Representa una empresa cliente (tenant) con su BD independiente"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(primary_key=True)
    name: str = Field(index=True, unique=True)  # "EmpresaX"
    nit: str = Field(unique=True)  # NIT colombiano
    database_url: str  # postgresql://user:pass@rds-empresax.amazonaws.com:5432/empresax_prod
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
