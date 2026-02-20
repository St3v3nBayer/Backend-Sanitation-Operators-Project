from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ========================================
# APS SCHEMAS
# ========================================

class APSBase(BaseModel):
    """Base schema para APS"""
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    municipality: str
    department: str
    
    # Datos geográficos
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None
    centroid_calculation_method: str = "baricentro"
    
    # Distancia
    distance_to_landfill_km: float = Field(..., gt=0, description="Distancia al relleno en km")
    unpaved_road_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # Sitio disposición final
    landfill_name: Optional[str] = None
    landfill_location: Optional[str] = None
    uses_transfer_station: bool = False
    transfer_station_distance_km: Optional[float] = None
    
    # Configuración
    segment: int = Field(default=2, ge=1, le=2)
    is_coastal_municipality: bool = False
    billing_type: str = "acueducto"
    billing_frequency: str = "monthly"
    
    @field_validator('billing_type')
    @classmethod
    def validate_billing_type(cls, v):
        if v not in ["acueducto", "energia"]:
            raise ValueError("billing_type debe ser 'acueducto' o 'energia'")
        return v


class APSCreate(APSBase):
    """Schema para crear APS"""
    company_id: int


class APSUpdate(BaseModel):
    """Schema para actualizar APS"""
    name: Optional[str] = None
    municipality: Optional[str] = None
    department: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None
    distance_to_landfill_km: Optional[float] = None
    unpaved_road_percentage: Optional[float] = None
    landfill_name: Optional[str] = None
    uses_transfer_station: Optional[bool] = None
    transfer_station_distance_km: Optional[float] = None
    segment: Optional[int] = None
    is_coastal_municipality: Optional[bool] = None
    billing_type: Optional[str] = None
    is_active: Optional[bool] = None


class APSRead(APSBase):
    """Schema para leer APS"""
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========================================
# MONTHLY DATA SCHEMAS
# ========================================

class APSMonthlyDataBase(BaseModel):
    """Base schema para datos mensuales"""
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$', description="Formato: YYYY-MM")
    
    # Suscriptores
    num_subscribers_total: int = Field(..., gt=0)
    num_subscribers_occupied: int = Field(..., ge=0)
    num_subscribers_vacant: int = Field(..., ge=0)
    num_subscribers_large_producers: int = Field(default=0, ge=0)
    
    # Distribución por estrato
    subscribers_stratum_1: int = Field(default=0, ge=0)
    subscribers_stratum_2: int = Field(default=0, ge=0)
    subscribers_stratum_3: int = Field(default=0, ge=0)
    subscribers_stratum_4: int = Field(default=0, ge=0)
    subscribers_stratum_5: int = Field(default=0, ge=0)
    subscribers_stratum_6: int = Field(default=0, ge=0)
    subscribers_commercial: int = Field(default=0, ge=0)
    
    # Toneladas
    tons_collected_non_recyclable: float = Field(..., ge=0)
    tons_collected_sweeping: float = Field(default=0.0, ge=0)
    tons_collected_urban_cleaning: float = Field(default=0.0, ge=0)
    tons_collected_recyclable: float = Field(default=0.0, ge=0)
    tons_rejection_recycling: float = Field(default=0.0, ge=0)
    
    # Limpieza urbana
    trees_pruned: int = Field(default=0, ge=0)
    cost_tree_pruning: float = Field(default=0.0, ge=0)
    grass_area_cut_m2: float = Field(default=0.0, ge=0)
    public_areas_washed_m2: float = Field(default=0.0, ge=0)
    beach_cleaning_m2: float = Field(default=0.0, ge=0)
    baskets_installed: int = Field(default=0, ge=0)
    baskets_maintained: int = Field(default=0, ge=0)
    
    # Barrido
    sweeping_length_km: float = Field(default=0.0, ge=0)
    sweeping_area_m2: float = Field(default=0.0, ge=0)
    
    # Disposición final
    tons_received_landfill: float = Field(..., ge=0)
    
    # Lixiviados
    leachate_volume_m3: float = Field(default=0.0, ge=0)
    leachate_treatment_scenario: int = Field(default=2, ge=1, le=5)
    environmental_tax_rate: float = Field(default=0.0, ge=0)
    
    # Flota
    fleet_average_age_years: float = Field(default=0.0, ge=0)
    fleet_daily_shifts: int = Field(default=1, ge=1, le=3)
    
    # Metadatos
    notes: Optional[str] = None


class APSMonthlyDataCreate(APSMonthlyDataBase):
    """Schema para crear datos mensuales"""
    aps_id: int
    
    @field_validator('period')
    @classmethod
    def extract_year_month(cls, v):
        # Extrae año y mes del período
        return v


class APSMonthlyDataRead(APSMonthlyDataBase):
    """Schema para leer datos mensuales"""
    id: int
    aps_id: int
    year: int
    month: int
    verified: bool
    verified_by: Optional[int]
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========================================
# TARIFF CALCULATION SCHEMAS
# ========================================

class TariffCalculationRequest(BaseModel):
    """Schema para solicitar un cálculo de tarifa"""
    aps_id: int
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    calculation_type: str = Field(default="official")
    
    # Para simulaciones
    is_simulation: bool = False
    simulation_name: Optional[str] = None
    simulation_data: Optional[dict] = None  # Datos a sobrescribir para la simulación
    
    # Factores de subsidio/contribución (opcional, usa defaults si no se provee)
    subsidy_contribution_factors: Optional[dict] = None
    
    @field_validator('calculation_type')
    @classmethod
    def validate_calculation_type(cls, v):
        if v not in ["official", "simulation", "test"]:
            raise ValueError("calculation_type debe ser 'official', 'simulation' o 'test'")
        return v


class TariffBreakdown(BaseModel):
    """Desglose detallado de una tarifa"""
    # Fijos
    cft: float
    ccs: float
    clus: float
    cbls: float
    
    # Variables
    cvna: float
    crt: float
    cdf: float
    ctl: float
    
    # Aprovechamiento
    vba: float
    
    # Toneladas
    trbl: float
    trlu: float
    trra: float
    tra: float


class TariffCalculationRead(BaseModel):
    """Schema para leer resultado de cálculo"""
    id: int
    aps_id: int
    period: str
    calculation_type: str
    calculation_date: datetime
    
    # Costos principales
    breakdown: TariffBreakdown
    
    # Tarifas por estrato
    tariff_stratum_1_base: float
    tariff_stratum_2_base: float
    tariff_stratum_3_base: float
    tariff_stratum_4_base: float
    tariff_stratum_5_base: float
    tariff_stratum_6_base: float
    tariff_commercial_base: float
    
    tariff_stratum_1_final: float
    tariff_stratum_2_final: float
    tariff_stratum_3_final: float
    tariff_stratum_4_final: float
    tariff_stratum_5_final: float
    tariff_stratum_6_final: float
    tariff_commercial_final: float
    
    # Validaciones
    validations: dict
    
    # Metadatos
    is_simulation: bool
    simulation_name: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class TariffComparisonRequest(BaseModel):
    """Schema para comparar dos cálculos"""
    calculation_id_1: int
    calculation_id_2: int


class TariffComparisonResult(BaseModel):
    """Resultado de comparación entre dos cálculos"""
    calculation_1: TariffCalculationRead
    calculation_2: TariffCalculationRead
    
    differences: dict  # Diferencias calculadas
    percentage_changes: dict  # Cambios porcentuales
