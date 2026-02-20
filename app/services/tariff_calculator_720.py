"""
Calculadora de Tarifas según Resolución CRA 720 de 2015

Este módulo implementa toda la metodología tarifaria establecida
en la Resolución 720 de 2015 para el servicio público de aseo.

Referencias:
- Resolución CRA 720 de 2015
- Decreto 1077 de 2015
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import math


class TariffCalculator720:
    """
    Calculadora de tarifas conforme a Resolución CRA 720 de 2015
    
    Implementa todas las fórmulas y metodologías de la resolución
    con referencias específicas a los artículos aplicados.
    """
    
    # ========================================
    # CONSTANTES (PRECIOS DICIEMBRE 2014)
    # ========================================
    
    # Costos de Comercialización (CCS) - Art. 14
    CCS_SEGMENT_1_WATER = 1223.39  # Segmento 1, facturación con acueducto
    CCS_SEGMENT_1_ENERGY = 1829.86  # Segmento 1, facturación con energía
    CCS_SEGMENT_2_WATER = 1368.85  # Segmento 2, facturación con acueducto
    CCS_SEGMENT_2_ENERGY = 1975.31  # Segmento 2, facturación con energía
    
    CCS_RECYCLING_INCREMENT = 0.30  # 30% incremento si hay aprovechamiento
    
    # Costos de Limpieza Urbana - Art. 15-20
    CCC_SEGMENT_1 = 57  # Corte de césped segmento 1 ($/m²)
    CCC_SEGMENT_2 = 86  # Corte de césped segmento 2 ($/m²)
    
    CLAV_BASE = 166  # Lavado áreas públicas base ($/m²)
    CLAV_WATER_FACTOR = 5.56  # Factor por precio agua
    
    CLP = 10789  # Limpieza playas ($/km)
    CLP_M2_TO_KM_FACTOR = 0.0007  # Factor conversión m² a km
    
    CCEI = 6276  # Instalación cestas ($/cesta-mes)
    CCEM = 571  # Mantenimiento cestas ($/cesta-mes)
    
    # Barrido y Limpieza - Art. 21
    CBL = 28985  # Costo por kilómetro barrido ($/km)
    CBL_M2_TO_KM_FACTOR = 0.002  # Factor conversión m² a km
    CBL_CAPITAL_PROPORTION = 0.32  # 32% es costo de capital
    
    # Recolección y Transporte - Art. 24
    # Función f1 (directo al relleno)
    F1_BASE = 64745
    F1_DISTANCE_FACTOR = 738
    F1_SCALE_FACTOR = 8683846
    
    # Función f2 (con estación de transferencia)
    F2_BASE = 87823
    F2_DISTANCE_FACTOR = 278
    F2_SCALE_FACTOR = 25211213
    
    CRT_COASTAL_ADJUSTMENT = 0.0197  # 1.97% ajuste municipios costeros
    CRT_CAPITAL_PROPORTION = 0.22  # 22% es costo de capital
    CRT_FLEET_AGE_DISCOUNT = 0.02  # 2% descuento por año de antigüedad
    
    UNPAVED_ROAD_MULTIPLIER = 1.25  # 1 km sin pavimento = 1.25 km pavimentado
    
    # Disposición Final - Art. 28
    CDF_VU_BASE = 18722
    CDF_VU_SCALE = 132924379
    CDF_VU_MAX = 139896
    
    CDF_PC_BASE = 242
    CDF_PC_SCALE = 11652352
    CDF_PC_MAX = 6185
    
    CDF_SMALL_LANDFILL_THRESHOLD = 2400  # toneladas/mes
    CDF_SMALL_LANDFILL_MAX_INCREASE = 0.10  # 10% máximo incremento
    
    # Tratamiento Lixiviados - Art. 32 y Anexo II
    CTL_SCENARIOS = {
        # Escenario 1: SS + MO
        1: {
            "vu_base": 898,
            "vu_scale": 44781608,
            "vu_max": 8139,
            "pc_base": 102,
            "pc_scale": 5875125,
            "pc_max": 1074
        },
        # Escenario 2: SS + MO + N
        2: {
            "vu_base": 1740,
            "vu_scale": 82290106,
            "vu_max": 14918,
            "pc_base": 167,
            "pc_scale": 8930368,
            "pc_max": 1628
        },
        # Escenario 3: SS + MO + SI + CO
        3: {
            "vu_base": 2212,
            "vu_scale": 103676696,
            "vu_max": 18787,
            "pc_base": 225,
            "pc_scale": 11561342,
            "pc_max": 2104
        },
        # Escenario 4: SS + MO + N + SI + CO
        4: {
            "vu_base": 2554,
            "vu_scale": 120381714,
            "vu_max": 21820,
            "pc_base": 261,
            "pc_scale": 13658195,
            "pc_max": 2488
        },
        # Escenario 5: Solo Recirculación
        5: {
            "recirculation_cost": 2348
        }
    }
    
    # Factores de Producción - Art. 42
    PRODUCTION_FACTORS = {
        "stratum_1": 0.79,
        "stratum_2": 0.86,
        "stratum_3": 0.90,
        "stratum_4": 1.00,
        "stratum_5": 1.22,
        "stratum_6": 1.50,
        "commercial": 2.44,  # Pequeños productores no residenciales
        "vacant": 0.00  # Inmuebles desocupados
    }
    
    def __init__(self, inflation_rate: float = 0.0):
        """
        Inicializa el calculador
        
        Args:
            inflation_rate: Tasa de inflación acumulada desde diciembre 2014
                           para actualizar costos. Por defecto 0.0.
        """
        self.inflation_rate = inflation_rate
    
    # ========================================
    # COSTO FIJO TOTAL (CFT) - Art. 11
    # ========================================
    
    def calculate_cft(
        self,
        ccs: float,
        clus: float,
        cbls: float
    ) -> float:
        """
        Calcula el Costo Fijo Total por suscriptor
        
        Art. 11: CFT = CCS + CLUS + CBLS
        
        Args:
            ccs: Costo de Comercialización
            clus: Costo de Limpieza Urbana
            cbls: Costo de Barrido y Limpieza
            
        Returns:
            float: Costo Fijo Total ($/suscriptor-mes)
        """
        return ccs + clus + cbls
    
    def calculate_ccs(
        self,
        segment: int,
        billing_type: str,
        has_recycling: bool = False
    ) -> float:
        """
        Calcula el Costo de Comercialización por Suscriptor
        
        Art. 14: Costos diferenciados por segmento y tipo de facturación
        Parágrafo: +30% si existe aprovechamiento
        
        Args:
            segment: 1 o 2
            billing_type: "acueducto" o "energia"
            has_recycling: Si hay actividad de aprovechamiento
            
        Returns:
            float: Costo de Comercialización ($/suscriptor-mes)
        """
        # Seleccionar costo base según segmento y tipo facturación
        if segment == 1:
            base_cost = self.CCS_SEGMENT_1_WATER if billing_type == "acueducto" else self.CCS_SEGMENT_1_ENERGY
        else:  # segment == 2
            base_cost = self.CCS_SEGMENT_2_WATER if billing_type == "acueducto" else self.CCS_SEGMENT_2_ENERGY
        
        # Aplicar incremento si hay aprovechamiento
        if has_recycling:
            base_cost *= (1 + self.CCS_RECYCLING_INCREMENT)
        
        # Aplicar inflación
        return self._apply_inflation(base_cost)
    
    def calculate_clus(
        self,
        num_subscribers: int,
        tree_pruning_cost: float = 0.0,
        grass_area_m2: float = 0.0,
        washing_area_m2: float = 0.0,
        beach_area_m2: float = 0.0,
        baskets_installed: int = 0,
        baskets_maintained: int = 0,
        segment: int = 2,
        water_price_per_m3: float = 0.0
    ) -> Tuple[float, Dict]:
        """
        Calcula el Costo de Limpieza Urbana por Suscriptor
        
        Art. 15: CLUS incluye poda, corte césped, lavado, playas, cestas
        
        Args:
            num_subscribers: N - Número total de suscriptores
            tree_pruning_cost: Costo total de poda en el mes
            grass_area_m2: Metros² de césped cortado
            washing_area_m2: Metros² de áreas lavadas
            beach_area_m2: Metros² de playas limpiadas
            baskets_installed: Número de cestas instaladas
            baskets_maintained: Número de cestas con mantenimiento
            segment: 1 o 2
            water_price_per_m3: Precio del m³ de agua para lavado
            
        Returns:
            Tuple[float, Dict]: (CLUS total, desglose por componente)
        """
        breakdown = {}
        
        # Poda de árboles (Art. 16)
        pruning_per_subscriber = tree_pruning_cost / num_subscribers if num_subscribers > 0 else 0
        breakdown["tree_pruning"] = pruning_per_subscriber
        
        # Corte de césped (Art. 17)
        ccc = self.CCC_SEGMENT_1 if segment == 1 else self.CCC_SEGMENT_2
        ccc = self._apply_inflation(ccc)
        grass_cost_total = grass_area_m2 * ccc
        grass_per_subscriber = grass_cost_total / num_subscribers if num_subscribers > 0 else 0
        breakdown["grass_cutting"] = grass_per_subscriber
        
        # Lavado de áreas públicas (Art. 18)
        clav = self._apply_inflation(self.CLAV_BASE + self.CLAV_WATER_FACTOR * (water_price_per_m3 / 1000))
        washing_cost_total = washing_area_m2 * clav
        washing_per_subscriber = washing_cost_total / num_subscribers if num_subscribers > 0 else 0
        breakdown["area_washing"] = washing_per_subscriber
        
        # Limpieza de playas (Art. 19)
        beach_km = beach_area_m2 * self.CLP_M2_TO_KM_FACTOR
        clp = self._apply_inflation(self.CLP)
        beach_cost_total = beach_km * clp
        beach_per_subscriber = beach_cost_total / num_subscribers if num_subscribers > 0 else 0
        breakdown["beach_cleaning"] = beach_per_subscriber
        
        # Cestas - instalación y mantenimiento (Art. 20)
        ccei = self._apply_inflation(self.CCEI)
        ccem = self._apply_inflation(self.CCEM)
        baskets_cost_total = (baskets_installed * ccei) + (baskets_maintained * ccem)
        baskets_per_subscriber = baskets_cost_total / num_subscribers if num_subscribers > 0 else 0
        breakdown["baskets"] = baskets_per_subscriber
        
        # Total CLUS
        clus_total = sum(breakdown.values())
        
        return round(clus_total, 2), breakdown
    
    def calculate_cbls(
        self,
        sweeping_km: float,
        num_subscribers: int,
        has_public_contribution: bool = False
    ) -> float:
        """
        Calcula el Costo de Barrido y Limpieza por Suscriptor
        
        Art. 21: CBLS = (CBL × LBL) / N
        Parágrafo 4: Descuento 32% si hay aporte bajo condición
        
        Args:
            sweeping_km: Longitud barrida en kilómetros
            num_subscribers: N - Número total de suscriptores
            has_public_contribution: Si hay aporte público de equipos
            
        Returns:
            float: Costo de Barrido y Limpieza ($/suscriptor-mes)
        """
        cbl = self._apply_inflation(self.CBL)
        
        # Descuento si hay aporte público (Art. 21 Par. 4)
        if has_public_contribution:
            cbl *= (1 - self.CBL_CAPITAL_PROPORTION)
        
        total_cost = cbl * sweeping_km
        cbls = total_cost / num_subscribers if num_subscribers > 0 else 0
        
        return round(cbls, 2)
    
    # ========================================
    # COSTO VARIABLE (CVNA) - Art. 12
    # ========================================
    
    def calculate_cvna(
        self,
        crt: float,
        cdf: float,
        ctl: float
    ) -> float:
        """
        Calcula el Costo Variable por Tonelada de Residuos No Aprovechables
        
        Art. 12: CVNA = CRT + CDF + CTL
        
        Args:
            crt: Costo de Recolección y Transporte
            cdf: Costo de Disposición Final
            ctl: Costo de Tratamiento de Lixiviados
            
        Returns:
            float: Costo Variable ($/tonelada)
        """
        return crt + cdf + ctl
    
    def calculate_crt(
        self,
        distance_km: float,
        avg_tons_month: float,
        tolls_cost_month: float = 0.0,
        is_coastal: bool = False,
        uses_transfer_station: bool = False,
        transfer_distance_km: float = 0.0,
        fleet_age_years: float = 0.0,
        fleet_daily_shifts: int = 1,
        has_public_contribution: bool = False
    ) -> Tuple[float, Dict]:
        """
        Calcula el Costo de Recolección y Transporte
        
        Art. 24: CRT = MIN(f1, f2) + PRT
        f1 = directo al relleno
        f2 = con estación de transferencia
        
        Args:
            distance_km: Distancia efectiva al relleno (D)
            avg_tons_month: Promedio toneladas/mes recolectadas
            tolls_cost_month: Costo de peajes al mes
            is_coastal: Si es municipio costero (ajuste 1.97%)
            uses_transfer_station: Si usa estación de transferencia
            transfer_distance_km: Distancia relleno-transferencia
            fleet_age_years: Antigüedad promedio de flota
            fleet_daily_shifts: Turnos diarios (1 o 2+)
            has_public_contribution: Si hay aporte público de vehículos
            
        Returns:
            Tuple[float, Dict]: (CRT total, detalles del cálculo)
        """
        details = {}
        
        # Calcular f1 (directo)
        f1 = self._apply_inflation(
            self.F1_BASE + 
            (self.F1_DISTANCE_FACTOR * distance_km) + 
            (self.F1_SCALE_FACTOR / avg_tons_month if avg_tons_month > 0 else 0)
        )
        details["f1"] = round(f1, 2)
        
        # Calcular f2 (con transferencia)
        f2 = self._apply_inflation(
            self.F2_BASE + 
            (self.F2_DISTANCE_FACTOR * distance_km) + 
            (self.F2_SCALE_FACTOR / avg_tons_month if avg_tons_month > 0 else 0)
        )
        details["f2"] = round(f2, 2)
        
        # Seleccionar función de mínimo costo
        if uses_transfer_station and transfer_distance_km > 0:
            crt_base = min(f1, f2)
            details["function_used"] = "f2" if f2 < f1 else "f1"
        else:
            crt_base = f1
            details["function_used"] = "f1"
        
        # Ajuste por salinidad (municipios costeros)
        if is_coastal:
            crt_base *= (1 + self.CRT_COASTAL_ADJUSTMENT)
            details["coastal_adjustment"] = True
        
        # Descuento por antigüedad de flota (Art. 27)
        fleet_discount = 0.0
        if fleet_age_years > 0:
            age_threshold = 12 if fleet_daily_shifts == 1 else 6
            if fleet_age_years > age_threshold:
                years_over = fleet_age_years - age_threshold
                fleet_discount = self.CRT_FLEET_AGE_DISCOUNT * years_over
                crt_base *= (1 - fleet_discount)
                details["fleet_age_discount"] = fleet_discount
        
        # Descuento por aporte público (Art. 26)
        if has_public_contribution:
            crt_base *= (1 - self.CRT_CAPITAL_PROPORTION)
            details["public_contribution_discount"] = True
        
        # Agregar peajes (PRT)
        prt = tolls_cost_month / avg_tons_month if avg_tons_month > 0 else 0
        crt_total = crt_base + prt
        details["tolls_per_ton"] = round(prt, 2)
        
        return round(crt_total, 2), details
    
    def calculate_cdf(
        self,
        avg_tons_landfill_month: float,
        is_small_landfill: bool = False,
        extended_postclosure_years: int = 0,
        has_public_contribution: bool = False
    ) -> Tuple[float, Dict]:
        """
        Calcula el Costo de Disposición Final
        
        Art. 28: CDF = CDF_VU + CDF_PC
        
        Args:
            avg_tons_landfill_month: Promedio toneladas recibidas/mes
            is_small_landfill: Si es <2,400 ton/mes y altura <9m
            extended_postclosure_years: Años adicionales a 10 de post-clausura
            has_public_contribution: Si hay aporte público
            
        Returns:
            Tuple[float, Dict]: (CDF total, detalles)
        """
        details = {}
        
        # CDF Vida Útil (20 años)
        cdf_vu = min(
            self._apply_inflation(18722 + (132924379 / avg_tons_landfill_month if avg_tons_landfill_month > 0 else 0)),
            self._apply_inflation(139896)
        )
        details["cdf_vu"] = round(cdf_vu, 2)
        
        # CDF Post-Clausura (10 años base)
        cdf_pc_base = min(
            self._apply_inflation(242 + (11652352 / avg_tons_landfill_month if avg_tons_landfill_month > 0 else 0)),
            self._apply_inflation(6185)
        )
        
        # Factor k para post-clausura extendida (Art. 28 Par. 5)
        if extended_postclosure_years > 0:
            k_factor = 0.8211 * math.log(10 + extended_postclosure_years) - 0.8954
            cdf_pc = cdf_pc_base * k_factor
            details["postclosure_extended"] = extended_postclosure_years
            details["k_factor"] = round(k_factor, 4)
        else:
            cdf_pc = cdf_pc_base
        
        details["cdf_pc"] = round(cdf_pc, 2)
        
        # Total CDF
        cdf_total = cdf_vu + cdf_pc
        
        # Ajuste para rellenos pequeños (Art. 28 Par. 2)
        if is_small_landfill and avg_tons_landfill_month < self.CDF_SMALL_LANDFILL_THRESHOLD:
            adjustment = cdf_total * self.CDF_SMALL_LANDFILL_MAX_INCREASE
            cdf_total += adjustment
            details["small_landfill_adjustment"] = round(adjustment, 2)
        
        # Descuento por aporte público (Art. 29)
        if has_public_contribution:
            # El descuento varía según tamaño: 21%, 32% o 37%
            # Por simplicidad, usamos 32% (promedio)
            discount_rate = 0.32
            cdf_total *= (1 - discount_rate)
            details["public_contribution_discount"] = True
            details["discount_rate"] = discount_rate
        
        return round(cdf_total, 2), details
    
    def calculate_ctl(
        self,
        leachate_volume_m3: float,
        avg_tons_landfill_month: float,
        scenario: int = 2,
        environmental_tax: float = 0.0,
        extended_postclosure_years: int = 0,
        has_public_contribution: bool = False
    ) -> Tuple[float, Dict]:
        """
        Calcula el Costo de Tratamiento de Lixiviados
        
        Art. 32: CTL = ((CTLM × VL) + CMTLX) / QRS
        
        Args:
            leachate_volume_m3: Volumen promedio lixiviados m³/mes
            avg_tons_landfill_month: Promedio toneladas en relleno/mes
            scenario: Escenario de tratamiento 1-5 (Anexo II)
            environmental_tax: Tasa ambiental $/m³
            extended_postclosure_years: Años adicionales post-clausura
            has_public_contribution: Si hay aporte público
            
        Returns:
            Tuple[float, Dict]: (CTL por tonelada, detalles)
        """
        details = {"scenario": scenario}
        
        # Escenario 5: Solo recirculación
        if scenario == 5:
            ctlm = self._apply_inflation(self.CTL_SCENARIOS[5]["recirculation_cost"])
            details["ctlm"] = round(ctlm, 2)
            ctl_total = (ctlm * leachate_volume_m3) / avg_tons_landfill_month if avg_tons_landfill_month > 0 else 0
            return round(ctl_total, 2), details
        
        # Escenarios 1-4
        scenario_data = self.CTL_SCENARIOS[scenario]
        
        # CTLM Vida Útil
        ctlm_vu = min(
            self._apply_inflation(scenario_data["vu_base"] + (scenario_data["vu_scale"] / leachate_volume_m3 if leachate_volume_m3 > 0 else 0)),
            self._apply_inflation(scenario_data["vu_max"])
        )
        details["ctlm_vu"] = round(ctlm_vu, 2)
        
        # CTLM Post-Clausura
        ctlm_pc_base = min(
            self._apply_inflation(scenario_data["pc_base"] + (scenario_data["pc_scale"] / leachate_volume_m3 if leachate_volume_m3 > 0 else 0)),
            self._apply_inflation(scenario_data["pc_max"])
        )
        
        # Factor k para post-clausura extendida
        if extended_postclosure_years > 0:
            k_factor = 0.8415 * math.log(10 + extended_postclosure_years) - 0.9429
            ctlm_pc = ctlm_pc_base * k_factor
            details["k_factor"] = round(k_factor, 4)
        else:
            ctlm_pc = ctlm_pc_base
        
        details["ctlm_pc"] = round(ctlm_pc, 2)
        
        # CTLM Total
        ctlm = ctlm_vu + ctlm_pc
        details["ctlm"] = round(ctlm, 2)
        
        # Costo total incluyendo tasa ambiental
        total_cost = (ctlm * leachate_volume_m3) + (environmental_tax * leachate_volume_m3)
        details["environmental_tax_total"] = round(environmental_tax * leachate_volume_m3, 2)
        
        # CTL por tonelada
        ctl_per_ton = total_cost / avg_tons_landfill_month if avg_tons_landfill_month > 0 else 0
        
        # Descuento por aporte público (Art. 33)
        if has_public_contribution:
            # Descuento varía por escenario: 38%, 49%, 47%, 46%, 80%
            discount_rates = {1: 0.38, 2: 0.49, 3: 0.47, 4: 0.46, 5: 0.80}
            discount_rate = discount_rates.get(scenario, 0.0)
            ctl_per_ton *= (1 - discount_rate)
            details["public_contribution_discount"] = True
            details["discount_rate"] = discount_rate
        
        return round(ctl_per_ton, 2), details
    
    # ========================================
    # APROVECHAMIENTO - Art. 34
    # ========================================
    
    def calculate_vba(
        self,
        crt_avg: float,
        cdf_avg: float,
        incentive_discount: float = 0.0
    ) -> float:
        """
        Calcula el Valor Base de Aprovechamiento
        
        Art. 34: VBA = (CRT_p + CDF_p) × (1 - DINC)
        
        Args:
            crt_avg: CRT promedio ponderado del municipio
            cdf_avg: CDF promedio ponderado del municipio
            incentive_discount: DINC - Descuento incentivo (0-0.04)
            
        Returns:
            float: Valor Base Aprovechamiento ($/tonelada)
        """
        vba = (crt_avg + cdf_avg) * (1 - incentive_discount)
        return round(vba, 2)
    
    # ========================================
    # TONELADAS POR SUSCRIPTOR - Art. 40, 41
    # ========================================
    
    def calculate_tons_per_subscriber_common(
        self,
        tons_sweeping_month: float,
        tons_urban_cleaning_month: float,
        tons_rejection_month: float,
        tons_recycled_month: float,
        num_subscribers_total: int,
        num_subscribers_vacant: int = 0,
        num_subscribers_large_producers: int = 0
    ) -> Dict[str, float]:
        """
        Calcula toneladas comunes por suscriptor (Art. 40)
        
        Estas toneladas aplican a TODOS los suscriptores.
        
        Args:
            tons_sweeping_month: QBL - Toneladas barrido y limpieza
            tons_urban_cleaning_month: QLU - Toneladas limpieza urbana
            tons_rejection_month: QR - Toneladas rechazo aprovechamiento
            tons_recycled_month: QA - Toneladas aprovechadas
            num_subscribers_total: N - Total suscriptores
            num_subscribers_vacant: ND - Suscriptores desocupados
            num_subscribers_large_producers: NA - Grandes productores con aforo
            
        Returns:
            Dict con TRBL, TRLU, TRRA, TRA
        """
        n = num_subscribers_total
        n_occupied = n - num_subscribers_vacant
        n_available_recycling = n_occupied - num_subscribers_large_producers
        
        return {
            "trbl": round(tons_sweeping_month / n, 6) if n > 0 else 0,
            "trlu": round(tons_urban_cleaning_month / n, 6) if n > 0 else 0,
            "trra": round(tons_rejection_month / n_occupied, 6) if n_occupied > 0 else 0,
            "tra": round(tons_recycled_month / n_available_recycling, 6) if n_available_recycling > 0 else 0
        }
    
    def calculate_trna_by_stratum(
        self,
        tons_non_recyclable_aps: float,
        tons_rejection: float,
        subscribers_by_stratum: Dict[str, int],
        num_subscribers_vacant: int = 0,
        tons_weighed_total: float = 0.0
    ) -> Dict[str, float]:
        """
        Calcula TRNA por tipo de suscriptor (Art. 41)
        
        Art. 41: TRNA_u = ((QNA - QR - ΣTAFNA) × F_u) / Σ((n_u - na_u - nD_u) × F_u)
        
        Args:
            tons_non_recyclable_aps: QNA - Toneladas no aprovechables del APS
            tons_rejection: QR - Toneladas de rechazo
            subscribers_by_stratum: Número de suscriptores por estrato
            num_subscribers_vacant: Suscriptores desocupados
            tons_weighed_total: Toneladas con aforo (grandes productores)
            
        Returns:
            Dict con TRNA por cada estrato
        """
        # Toneladas disponibles para distribuir
        available_tons = tons_non_recyclable_aps - tons_rejection - tons_weighed_total
        
        # Calcular denominador: Σ((n_u - nD_u) × F_u)
        denominator = 0.0
        for stratum, count in subscribers_by_stratum.items():
            if stratum == "vacant":
                continue  # Los desocupados no cuentan
            factor = self.PRODUCTION_FACTORS.get(stratum, 1.0)
            # Restar proporcional de desocupados si los hay
            effective_count = count
            denominator += effective_count * factor
        
        # Calcular TRNA para cada estrato
        trna_by_stratum = {}
        if denominator > 0:
            for stratum in subscribers_by_stratum.keys():
                if stratum == "vacant":
                    trna_by_stratum[stratum] = 0.0
                else:
                    factor = self.PRODUCTION_FACTORS.get(stratum, 1.0)
                    trna = (available_tons * factor) / denominator
                    trna_by_stratum[stratum] = round(trna, 6)
        else:
            for stratum in subscribers_by_stratum.keys():
                trna_by_stratum[stratum] = 0.0
        
        return trna_by_stratum
    
    # ========================================
    # TARIFA FINAL - Art. 39
    # ========================================
    
    def calculate_final_tariff(
        self,
        cft: float,
        cvna: float,
        vba: float,
        trbl: float,
        trlu: float,
        trra: float,
        tra: float,
        trna: float,
        subsidy_contribution_factor: float = 0.0
    ) -> Tuple[float, float]:
        """
        Calcula la Tarifa Final por Suscriptor (Art. 39)
        
        TFS = (CFT + CVNA × (TRBL + TRLU + TRNA + TRRA) + (VBA × TRA)) × (1 ± FCS)
        
        Args:
            cft: Costo Fijo Total
            cvna: Costo Variable No Aprovechable
            vba: Valor Base Aprovechamiento
            trbl: Toneladas barrido/limpieza
            trlu: Toneladas limpieza urbana
            trra: Toneladas rechazo aprovechamiento
            tra: Toneladas aprovechadas
            trna: Toneladas no aprovechables (por estrato)
            subsidy_contribution_factor: FCS (negativo=subsidio, positivo=contribución)
            
        Returns:
            Tuple[float, float]: (Tarifa base, Tarifa final con subsidio/contribución)
        """
        # Componente fijo
        fixed_component = cft
        
        # Componente variable no aprovechable
        variable_component = cvna * (trbl + trlu + trna + trra)
        
        # Componente aprovechamiento
        recycling_component = vba * tra
        
        # Tarifa base (sin subsidios/contribuciones)
        tariff_base = fixed_component + variable_component + recycling_component
        
        # Aplicar subsidio/contribución
        tariff_final = tariff_base * (1 + subsidy_contribution_factor)
        
        return round(tariff_base, 2), round(tariff_final, 2)
    
    # ========================================
    # UTILIDADES
    # ========================================
    
    def _apply_inflation(self, base_value: float) -> float:
        """Aplica inflación a un valor base de diciembre 2014"""
        return base_value * (1 + self.inflation_rate)
    
    def get_formula_reference(self, component: str) -> str:
        """
        Retorna la referencia al artículo de la Resolución 720
        para un componente específico.
        
        Args:
            component: Nombre del componente (CFT, CCS, CRT, etc.)
            
        Returns:
            str: Referencia al artículo
        """
        references = {
            "CFT": "Artículo 11",
            "CCS": "Artículo 14",
            "CLUS": "Artículo 15",
            "CBLS": "Artículo 21",
            "CVNA": "Artículo 12",
            "CRT": "Artículo 24",
            "CDF": "Artículo 28",
            "CTL": "Artículo 32",
            "VBA": "Artículo 34",
            "TRNA": "Artículo 41",
            "TFS": "Artículo 39"
        }
        return references.get(component, "No disponible")
