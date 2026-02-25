from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Company(SQLModel, table=True):
    """
    Company model - represents a single organization.
    Each company gets its own EC2/ECS instance with isolated database.
    """
    __tablename__ = "company"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Company information
    name: str = Field(unique=True, index=True)
    nit: str = Field(unique=True, index=True)  # Colombian NIT
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = Field(default=None, unique=True)
    
    # Control
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
