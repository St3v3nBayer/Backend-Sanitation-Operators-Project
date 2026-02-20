from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import field_validator


class APS(SQLModel, table=True):
    """
    APS - Área de Prestación del Servicio
    
    Según Resolución CRA 720 de 2015, Artículo 4:
    "Área geográfica del municipio y/o distrito en la cual la persona 
    prestadora de la actividad de recolección y transporte de residuos 
    no aprovechables presta el servicio."
    
    Cada empresa de limpieza puede tener una o más APS.
    """
    __tablename__ = "aps"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación con la empresa
    company_id: int = Field(foreign_key="company.id", index=True)
    
    # Identificación del APS
    name: str = Field(index=True)  # Ej: "APS Norte", "APS Centro"
    code: str = Field(unique=True, index=True)  # Código único interno
    
    # Ubicación geográfica
    municipality: str  # Municipio o distrito
    department: str  # Departamento
    
    # Datos del centroide (Art. 9)
    centroid_lat: Optional[float] = None  # Latitud del centroide
    centroid_lon: Optional[float] = None  # Longitud del centroide
    centroid_calculation_method: str = Field(default="baricentro")  # "baricentro" o "limite_aps"
    
    # Distancia al sitio de disposición final (Art. 24)
    distance_to_landfill_km: float  # Distancia D en kilómetros
    unpaved_road_percentage: float = Field(default=0.0)  # % de vías sin pavimentar
    
    # Datos del sitio de disposición final
    landfill_name: Optional[str] = None
    landfill_location: Optional[str] = None
    uses_transfer_station: bool = Field(default=False)
    transfer_station_distance_km: Optional[float] = None
    
    # Segmentación (Art. 5)
    segment: int = Field(default=2)  # 1 o 2
    
    # Características especiales
    is_coastal_municipality: bool = Field(default=False)  # Para ajuste de salinidad (1.97%)
    
    # Facturación
    billing_type: str = Field(default="acueducto")  # "acueducto" o "energia"
    billing_frequency: str = Field(default="monthly")  # "monthly" o "bimonthly"
    
    # Estado
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('segment')
    @classmethod
    def validate_segment(cls, v):
        if v not in [1, 2]:
            raise ValueError("Segmento debe ser 1 o 2")
        return v
    
    @field_validator('billing_type')
    @classmethod
    def validate_billing_type(cls, v):
        if v not in ["acueducto", "energia"]:
            raise ValueError("Tipo de facturación debe ser 'acueducto' o 'energia'")
        return v
    
    @field_validator('unpaved_road_percentage')
    @classmethod
    def validate_unpaved_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Porcentaje de vías sin pavimentar debe estar entre 0 y 100")
        return v
    
    def get_effective_distance(self) -> float:
        """
        Calcula la distancia efectiva ajustada por vías sin pavimentar.
        
        Según Art. 24: "Cada kilómetro de vía despavimentada equivaldrá 
        a 1,25 kilómetros de vía pavimentada."
        
        Returns:
            float: Distancia efectiva en km
        """
        if self.unpaved_road_percentage == 0:
            return self.distance_to_landfill_km
        
        paved_km = self.distance_to_landfill_km * (1 - self.unpaved_road_percentage / 100)
        unpaved_km = self.distance_to_landfill_km * (self.unpaved_road_percentage / 100)
        
        effective_distance = paved_km + (unpaved_km * 1.25)
        return round(effective_distance, 2)
