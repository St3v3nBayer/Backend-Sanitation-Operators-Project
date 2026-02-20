"""
Schemas para Cálculo y Validación de Tarifas según Resolución 720
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class TariffCalculationInput(BaseModel):
    """
    Input para calcular tarifa (validador o creación)
    Contiene todos los parámetros que el tarifador proporciona
    """
    
    # ========================================
    # COSTO FIJO TOTAL (CFT)
    # ========================================
    segment: int = Field(1, ge=1, le=2, description="Segmento 1 o 2")
    billing_type: str = Field("acueducto", description="acueducto o energia")
    has_recycling: bool = Field(False, description="¿Hay aprovechamiento?")
    
    # Limpieza urbana
    green_area_m2: float = Field(0.0, ge=0, description="m² de áreas verdes")
    beach_km: float = Field(0.0, ge=0, description="km de playas (si aplica)")
    baskets_count: int = Field(0, ge=0, description="Número de cestas")
    
    # Barrido
    sweep_area_m2: float = Field(0.0, ge=0, description="m² a barrer")
    
    # ========================================
    # COSTO VARIABLE NO APROVECHABLE (CVNA)
    # ========================================
    
    # Recolección y Transporte (CRT)
    crt_function: str = Field("f1", description="f1 (directo) o f2 (transferencia)")
    distance_km: float = Field(1.0, ge=0.5, description="Distancia promedio a relleno")
    unpaved_roads_km: float = Field(0.0, ge=0, description="km sin pavimentar")
    fleet_age_years: int = Field(0, ge=0, le=30, description="Antigüedad flota")
    is_coastal: bool = Field(False, description="¿Municipio costero?")
    avg_tons_collected: float = Field(10.0, gt=0, description="Tons/mes promedio") 
    tolls_per_ton: float = Field(0.0, ge=0, description="Peajes $/ton")
    
    # Disposición Final (CDF)
    avg_tons_landfill: float = Field(10.0, gt=0, description="Tons en relleno/mes")
    is_small_landfill: bool = Field(False, description="¿Relleno < 2,400 ton/mes?")
    
    # Tratamiento Lixiviados (CTL)
    ctl_scenario: int = Field(1, ge=1, le=5, description="Escenario de tratamiento 1-5")
    leachate_volume_m3: float = Field(100.0, gt=0, description="Volumen lixiviados m³/mes")
    
    # ========================================
    # TONELADAS POR SUSCRIPTOR
    # ========================================
    tons_per_subscriber_sweep: float = Field(0.1, gt=0, description="Tons/suscriptor barrido")
    tons_per_subscriber_urban: float = Field(0.05, gt=0, description="Tons/suscriptor limpieza")
    tons_per_subscriber_recycled: float = Field(0.02, gt=0, description="Tons/suscriptor recicladas")
    tons_per_subscriber_rejected: float = Field(0.01, gt=0, description="Tons/suscriptor rechazo")
    tons_per_subscriber_non_recoverable: float = Field(0.05, gt=0, description="Tons/suscriptor no aprovechables")
    
    # ========================================
    # SUBSIDY / CONTRIBUTION
    # ========================================
    subsidy_contribution_factor: float = Field(0.0, ge=-1, le=1, description="Factor FCS (negativo=subsidio)")
    
    # ========================================
    # INFLACIÓN (OPCIONAL)
    # ========================================
    inflation_rate: float = Field(0.0, ge=0, le=1, description="Tasa de inflación anual")
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment": 1,
                "billing_type": "acueducto",
                "has_recycling": True,
                "green_area_m2": 5000,
                "beach_km": 0,
                "baskets_count": 50,
                "sweep_area_m2": 10000,
                "crt_function": "f1",
                "distance_km": 15.5,
                "unpaved_roads_km": 2.0,
                "fleet_age_years": 5,
                "is_coastal": False,
                "avg_tons_collected": 100,
                "tolls_per_ton": 500,
                "avg_tons_landfill": 95,
                "is_small_landfill": False,
                "ctl_scenario": 3,
                "leachate_volume_m3": 500,
                "tons_per_subscriber_sweep": 0.12,
                "tons_per_subscriber_urban": 0.08,
                "tons_per_subscriber_recycled": 0.05,
                "tons_per_subscriber_rejected": 0.02,
                "tons_per_subscriber_non_recoverable": 0.06,
                "subsidy_contribution_factor": 0.0,
                "inflation_rate": 0.03
            }
        }


class ComponentBreakdown(BaseModel):
    """Desglose de un componente tarifario"""
    name: str
    value: float
    description: Optional[str] = None
    details: Optional[Dict[str, float]] = None


class TariffCalculationResult(BaseModel):
    """
    Resultado del cálculo de tarifa (detallado)
    Muestra todos los componentes para auditoría y validación
    """
    
    # CFT Components
    ccs: float
    clus: float = Field(description="Limpieza urbana")
    cbls: float = Field(description="Barrido y limpieza")
    cft: float = Field(description="Costo Fijo Total")
    cft_breakdown: List[ComponentBreakdown]
    
    # CVNA Components
    crt: float = Field(description="Recolección y transporte")
    crt_details: Dict[str, float] = Field(description="Desglose CRT: f1/f2, ajustes")
    cdf: float = Field(description="Disposición final")
    cdf_details: Dict[str, float] = Field(description="Desglose CDF: VU, PC")
    ctl: float = Field(description="Tratamiento lixiviados")
    ctl_details: Dict[str, float] = Field(description="Escenario, volumen")
    cvna: float = Field(description="Costo Variable No Aprovechable")
    
    # VBA
    vba: float = Field(description="Valor Base Aprovechamiento")
    
    # Toneladas
    total_tons_non_recyclable: float
    total_tons_recyclable: float
    
    # Final
    tariff_base: float = Field(description="Tarifa base sin subsidios")
    subsidy_contribution: float = Field(description="Subsidy/contribution amount")
    tariff_final: float = Field(description="Tarifa final con subsidios/contribuciones")
    
    # Auditoría
    formula_notes: List[str] = Field(description="Notas de fórmula aplicada")
    applied_adjustments: List[str] = Field(description="Ajustes aplicados")
    
    class Config:
        json_schema_extra = {
            "description": "Resultado completo de cálculo tarifario con todos los componentes"
        }


class CreateTariffRequest(BaseModel):
    """Request para crear tarifa mensual oficial"""
    
    aps_id: int = Field(description="ID del APS")
    period: str = Field(description="Período YYYY-MM, ej: 2026-01")
    calculation_type: str = Field("official", description="official, simulation, test")
    
    # Inputs del cálculo
    input_data: TariffCalculationInput
    
    # Notas del tarifador
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "aps_id": 1,
                "period": "2026-01",
                "calculation_type": "official",
                "input_data": {},  # Ver TariffCalculationInput
                "notes": "Validado contra histórico 2025"
            }
        }


class SimulateTariffRequest(BaseModel):
    """Request para simular/validar tarifa (no guarda)"""
    
    aps_id: int = Field(description="ID del APS (opcional, solo para contexto)")
    period: Optional[str] = None
    input_data: TariffCalculationInput
    
    class Config:
        json_schema_extra = {
            "description": "Simular tarifa sin guardar en BD"
        }


class TariffHistoryItem(BaseModel):
    """Item en histórico de tarifas"""
    
    id: int
    period: str
    tariff_final: float
    calculated_by: Optional[int] = None
    calculation_date: datetime
    calculation_type: str
    notes: Optional[str] = None


class TariffHistoryResponse(BaseModel):
    """
    Histórico de tarifas de un APS
    Útil para validar tendencias y cambios
    """
    
    aps_id: int
    total_count: int
    tariffs: List[TariffHistoryItem]
