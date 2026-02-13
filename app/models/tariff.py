from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Tariff(SQLModel, table=True):
    """
    Tariff Formula - Resolución 720
    
    Almacena fórmulas de cálculo de tarifas por empresa/tenant.
    Permite variables dinámicas y fórmulas customizables.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    company_id: Optional[int] = Field(default=None, index=True)  # Si es null = aplica a todo el tenant
    
    # Metadata
    name: str = Field(index=True)  # "Tarifa Acueducto 2026", "Tarifa Alcantarillado 2026"
    description: Optional[str] = None
    year: int = Field(index=True)  # Año de vigencia
    period: str = Field(default="annual")  # "monthly", "annual", "quarterly"
    
    # Tipo de tarifa
    tariff_type: str  # "water", "sewerage", "cleaning", "other"
    
    # Variables de entrada (JSON flexible)
    # Ejemplo: {"cubic_meters": 0, "users": 0, "area_m2": 0}
    input_variables: dict = Field(default_factory=dict, sa_type='jsonb')
    
    # Fórmula (puede ser simple o compleja)
    # Ejemplo: "fixed_fee + (cubic_meters * variable_fee) - (users * discount)"
    formula: str
    
    # Coeficientes/Parámetros
    # {"fixed_fee": 15000, "variable_fee": 2500, "discount": 500}
    parameters: dict = Field(default_factory=dict, sa_type='jsonb')
    
    # Estado
    active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
