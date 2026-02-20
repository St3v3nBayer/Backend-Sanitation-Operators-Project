from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from decimal import Decimal


class TariffCalculation(SQLModel, table=True):
    """
    Resultado de un cálculo tarifario según Resolución CRA 720 de 2015
    
    Almacena todos los componentes de la tarifa calculada,
    con trazabilidad completa para auditorías y reportes.
    """
    __tablename__ = "tariff_calculation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    company_id: int = Field(foreign_key="company.id", index=True)
    aps_id: int = Field(foreign_key="aps.id", index=True)
    
    # Identificación del cálculo
    calculation_type: str = Field(default="official")  # "official", "simulation", "test"
    period: str = Field(index=True)  # "2026-02"
    
    # Usuario que realizó el cálculo
    calculated_by: int = Field(foreign_key="user.id")
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    
    # ========================================
    # COSTO FIJO TOTAL (CFT) - Art. 11
    # ========================================
    cft: float  # Costo Fijo Total por suscriptor ($/suscriptor-mes)
    
    # Componentes del CFT
    ccs: float  # Comercialización (Art. 14)
    clus: float  # Limpieza Urbana (Art. 15)
    cbls: float  # Barrido y Limpieza (Art. 21)
    
    # Desglose detallado CLUS
    clus_breakdown: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {
    #   "tree_pruning": 0.0,
    #   "grass_cutting": 0.0,
    #   "area_washing": 0.0,
    #   "beach_cleaning": 0.0,
    #   "baskets_installation": 0.0,
    #   "baskets_maintenance": 0.0
    # }
    
    # ========================================
    # COSTO VARIABLE NO APROVECHABLE (CVNA) - Art. 12
    # ========================================
    cvna: float  # Costo Variable por tonelada ($/tonelada)
    
    # Componentes del CVNA
    crt: float  # Recolección y Transporte (Art. 24)
    cdf: float  # Disposición Final (Art. 28)
    ctl: float  # Tratamiento Lixiviados (Art. 32)
    
    # Desglose CRT
    crt_function_used: str = Field(default="f1")  # "f1" o "f2"
    crt_distance_km: float  # Distancia D utilizada
    crt_avg_tons: float  # QRT promedio
    crt_tolls: float = Field(default=0.0)  # PRT - Peajes
    crt_coastal_adjustment: bool = Field(default=False)  # Ajuste salinidad 1.97%
    crt_fleet_age_discount: float = Field(default=0.0)  # Descuento por antigüedad
    
    # Desglose CDF
    cdf_vu: float  # Vida útil (20 años)
    cdf_pc: float  # Post-clausura
    cdf_avg_tons_landfill: float  # QRS promedio
    cdf_adjustment_small_landfill: float = Field(default=0.0)  # Ajuste <2,400 ton/mes
    
    # Desglose CTL
    ctl_scenario: int  # 1-5
    ctl_volume_m3: float  # VL promedio
    ctl_environmental_tax: float  # CMTLX
    ctl_vu: float  # Vida útil
    ctl_pc: float  # Post-clausura
    
    # ========================================
    # VALOR BASE APROVECHAMIENTO (VBA) - Art. 34
    # ========================================
    vba: float  # Valor Base Aprovechamiento ($/tonelada)
    vba_incentive_discount: float = Field(default=0.0)  # DINC (hasta 4%)
    
    # ========================================
    # TONELADAS POR SUSCRIPTOR - Art. 40, 41
    # ========================================
    # Toneladas comunes (todos los suscriptores)
    trbl: float  # Barrido y limpieza por suscriptor
    trlu: float  # Limpieza urbana por suscriptor
    trra: float  # Rechazo aprovechamiento por suscriptor
    tra: float  # Aprovechadas por suscriptor
    
    # Toneladas no aprovechables por estrato (usuarios sin aforo)
    trna_stratum_1: float = Field(default=0.0)
    trna_stratum_2: float = Field(default=0.0)
    trna_stratum_3: float = Field(default=0.0)
    trna_stratum_4: float = Field(default=0.0)
    trna_stratum_5: float = Field(default=0.0)
    trna_stratum_6: float = Field(default=0.0)
    trna_commercial: float = Field(default=0.0)
    
    # ========================================
    # TARIFAS FINALES POR ESTRATO - Art. 39
    # ========================================
    # Sin subsidios/contribuciones
    tariff_stratum_1_base: float = Field(default=0.0)
    tariff_stratum_2_base: float = Field(default=0.0)
    tariff_stratum_3_base: float = Field(default=0.0)
    tariff_stratum_4_base: float = Field(default=0.0)
    tariff_stratum_5_base: float = Field(default=0.0)
    tariff_stratum_6_base: float = Field(default=0.0)
    tariff_commercial_base: float = Field(default=0.0)
    
    # Con subsidios/contribuciones aplicados
    tariff_stratum_1_final: float = Field(default=0.0)
    tariff_stratum_2_final: float = Field(default=0.0)
    tariff_stratum_3_final: float = Field(default=0.0)
    tariff_stratum_4_final: float = Field(default=0.0)
    tariff_stratum_5_final: float = Field(default=0.0)
    tariff_stratum_6_final: float = Field(default=0.0)
    tariff_commercial_final: float = Field(default=0.0)
    
    # Factores de subsidio/contribución aplicados
    subsidy_contribution_factors: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {
    #   "stratum_1": -0.7,  # 70% subsidio
    #   "stratum_2": -0.4,  # 40% subsidio
    #   "stratum_3": -0.15, # 15% subsidio
    #   "stratum_4": 0.0,   # Sin subsidio ni contribución
    #   "stratum_5": 0.2,   # 20% contribución
    #   "stratum_6": 0.2,   # 20% contribución
    #   "commercial": 0.3   # 30% contribución
    # }
    
    # ========================================
    # DATOS DE ENTRADA (SNAPSHOT)
    # ========================================
    input_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # Snapshot de los datos usados para el cálculo (trazabilidad)
    
    # ========================================
    # FÓRMULAS Y REFERENCIAS NORMATIVAS
    # ========================================
    formulas_used: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {
    #   "CFT": "CCS + CLUS + CBLS (Art. 11)",
    #   "CRT": "MIN(f1, f2) + PRT (Art. 24)",
    #   "CDF": "CDF_VU + CDF_PC (Art. 28)",
    #   ...
    # }
    
    regulatory_references: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {
    #   "CFT": ["Art. 11"],
    #   "CCS": ["Art. 14"],
    #   "CRT": ["Art. 24", "Art. 24 Par. 1", "Art. 27"],
    #   ...
    # }
    
    # ========================================
    # VALIDACIONES Y ALERTAS
    # ========================================
    validations: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # {
    #   "min_frequency_met": true,
    #   "compaction_density_ok": true,
    #   "within_max_costs": true,
    #   "alerts": [
    #     "Distancia >50km: considerar estación transferencia",
    #     "Flota >12 años: descuento aplicado"
    #   ]
    # }
    
    # ========================================
    # METADATOS
    # ========================================
    is_simulation: bool = Field(default=False)
    simulation_name: Optional[str] = None
    notes: Optional[str] = None
    
    # Para comparaciones
    comparison_with: Optional[int] = None  # FK a otro tariff_calculation_id
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "aps_id": 1,
                "period": "2026-02",
                "calculation_type": "official",
                "cft": 8250.0,
                "ccs": 1224.0,
                "clus": 3156.0,
                "cbls": 3870.0,
                "cvna": 35890.0,
                "crt": 22345.0,
                "cdf": 11230.0,
                "ctl": 2315.0,
                "vba": 1710.0,
                "tariff_stratum_4_base": 45850.0
            }
        }
