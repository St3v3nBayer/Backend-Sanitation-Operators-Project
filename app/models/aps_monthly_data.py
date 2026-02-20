from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from decimal import Decimal


class APSMonthlyData(SQLModel, table=True):
    """
    Datos operativos mensuales del APS
    
    Almacena la información mensual necesaria para el cálculo
    de tarifas según Resolución CRA 720 de 2015.
    
    Los promedios de 6 meses se calculan automáticamente
    según Art. 4 de la resolución.
    """
    __tablename__ = "aps_monthly_data"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación con APS
    aps_id: int = Field(foreign_key="aps.id", index=True)
    
    # Período (YYYY-MM)
    period: str = Field(index=True)  # "2026-02"
    year: int = Field(index=True)
    month: int = Field(index=True)
    
    # ========================================
    # DATOS DE SUSCRIPTORES (Art. 4)
    # ========================================
    num_subscribers_total: int  # N - Total de suscriptores
    num_subscribers_occupied: int  # Suscriptores ocupados
    num_subscribers_vacant: int  # ND - Desocupados
    num_subscribers_large_producers: int = Field(default=0)  # NA - Grandes productores con aforo
    
    # Distribución por estrato (residencial)
    subscribers_stratum_1: int = Field(default=0)
    subscribers_stratum_2: int = Field(default=0)
    subscribers_stratum_3: int = Field(default=0)
    subscribers_stratum_4: int = Field(default=0)
    subscribers_stratum_5: int = Field(default=0)
    subscribers_stratum_6: int = Field(default=0)
    subscribers_commercial: int = Field(default=0)  # Pequeños productores no residenciales
    
    # ========================================
    # TONELADAS RECOLECTADAS (Art. 24, 40, 47)
    # ========================================
    tons_collected_non_recyclable: float  # QNA_z - Toneladas no aprovechables recolectadas
    tons_collected_sweeping: float = Field(default=0.0)  # QBL - Toneladas de barrido y limpieza
    tons_collected_urban_cleaning: float = Field(default=0.0)  # QLU - Toneladas de limpieza urbana
    tons_collected_recyclable: float = Field(default=0.0)  # QA - Toneladas aprovechables
    tons_rejection_recycling: float = Field(default=0.0)  # QR - Rechazo del aprovechamiento
    
    # ========================================
    # ACTIVIDADES LIMPIEZA URBANA (Art. 15)
    # ========================================
    # Poda de árboles
    trees_pruned: int = Field(default=0)  # Número de árboles podados
    cost_tree_pruning: float = Field(default=0.0)  # Costo total poda en el mes
    
    # Corte de césped
    grass_area_cut_m2: float = Field(default=0.0)  # Metros² de césped cortado
    
    # Lavado de áreas públicas
    public_areas_washed_m2: float = Field(default=0.0)  # Metros² lavados
    
    # Limpieza de playas
    beach_cleaning_m2: float = Field(default=0.0)  # Metros² de playa limpiada
    beach_cleaning_km: float = Field(default=0.0)  # Convertido a km (m2 * 0.0007)
    
    # Cestas
    baskets_installed: int = Field(default=0)  # TI - Cestas instaladas nuevas
    baskets_maintained: int = Field(default=0)  # TM - Cestas con mantenimiento
    
    # ========================================
    # BARRIDO Y LIMPIEZA (Art. 21)
    # ========================================
    sweeping_length_km: float = Field(default=0.0)  # LBL - Kilómetros barridos
    sweeping_area_m2: float = Field(default=0.0)  # Áreas barridas (convertir a km)
    
    # ========================================
    # DISPOSICIÓN FINAL (Art. 28)
    # ========================================
    tons_received_landfill: float  # QRS - Toneladas recibidas en relleno sanitario
    
    # ========================================
    # TRATAMIENTO LIXIVIADOS (Art. 32)
    # ========================================
    leachate_volume_m3: float = Field(default=0.0)  # VL - Volumen lixiviados tratados
    leachate_treatment_scenario: int = Field(default=2)  # Escenario 1-5 (Anexo II)
    environmental_tax_rate: float = Field(default=0.0)  # CMTLX - Tasa ambiental $/m³
    
    # ========================================
    # COSTOS OPERATIVOS
    # ========================================
    operational_costs: dict = Field(default_factory=dict, sa_column=Column(JSON))
    # Estructura sugerida:
    # {
    #   "fuel_cost": 0.0,
    #   "labor_cost": 0.0,
    #   "maintenance_cost": 0.0,
    #   "tolls_cost": 0.0,  # PRT - Peajes
    #   "other_costs": 0.0
    # }
    
    # ========================================
    # FLOTA DE VEHÍCULOS (para descuentos Art. 27)
    # ========================================
    fleet_average_age_years: float = Field(default=0.0)  # Antigüedad promedio
    fleet_daily_shifts: int = Field(default=1)  # 1 o 2+ turnos diarios
    
    # ========================================
    # METADATOS
    # ========================================
    data_source: str = Field(default="manual")  # "manual", "imported", "api"
    verified: bool = Field(default=False)  # ¿Verificado por auditor?
    verified_by: Optional[int] = None  # FK a user_id del auditor
    verified_at: Optional[datetime] = None
    
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "aps_id": 1,
                "period": "2026-02",
                "year": 2026,
                "month": 2,
                "num_subscribers_total": 12450,
                "num_subscribers_occupied": 11800,
                "num_subscribers_vacant": 650,
                "tons_collected_non_recyclable": 850.5,
                "distance_to_landfill_km": 25.3,
                "trees_pruned": 45,
                "cost_tree_pruning": 850000.0,
                "grass_area_cut_m2": 2500.0,
                "tons_received_landfill": 920.3,
                "leachate_volume_m3": 1500.0,
                "leachate_treatment_scenario": 2
            }
        }
