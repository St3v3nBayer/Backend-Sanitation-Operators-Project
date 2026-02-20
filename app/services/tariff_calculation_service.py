"""
Servicio para Cálculo y Validación de Tarifas según Resolución 720
Orquesta el TariffCalculator720 y retorna resultados auditables para:
1. Validador: Simular tarifas históricas (sin guardar)
2. Creador: Crear tarifas mensuales oficiales (guardar en BD)
"""

from typing import Dict, Optional
from datetime import datetime
from sqlmodel import Session

from .tariff_calculator_720 import TariffCalculator720
from ..schemas.tariff_calculation import (
    TariffCalculationInput,
    TariffCalculationResult,
    ComponentBreakdown,
)
from ..models.tariff_calculation import TariffCalculation
from ..models.user import User
from ..models.aps import APS


class TariffCalculationService:
    """
    Orquesta el cálculo de tarifas según Res 720
    Transforma inputs → resultados auditables → guarda en BD (opcional)
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.calculator = TariffCalculator720()
    
    def calculate_tariff(
        self,
        input_data: TariffCalculationInput,
        current_user: Optional[User] = None
    ) -> TariffCalculationResult:
        """
        Calcula tarifa completa y retorna resultado detallado
        NO guarda en BD (es simulación/validación)
        
        Args:
            input_data: Parámetros del cálculo
            current_user: Usuario que realiza el cálculo (opcional)
            
        Returns:
            TariffCalculationResult: Resultado con todos componentes desglosados
        """
        
        # ========================================
        # 1. CALCULAR COMPONENTES FIJOS (CFT)
        # ========================================
        
        # CCS - Comercialización
        ccs = self.calculator.calculate_ccs(
            segment=input_data.segment,
            billing_type=input_data.billing_type,
            has_recycling=input_data.has_recycling
        )
        
        # CLUS - Limpieza Urbana
        clus = self.calculator.calculate_clus(
            segment=input_data.segment,
            green_area_m2=input_data.green_area_m2,
            beach_km=input_data.beach_km,
            baskets_count=input_data.baskets_count
        )
        
        # CBLS - Barrido y Limpieza
        cbls = self.calculator.calculate_cbls(
            area_m2=input_data.sweep_area_m2
        )
        
        # CFT = CCS + CLUS + CBLS
        cft = self.calculator.calculate_cft(
            ccs=ccs,
            clus=clus,
            cbls=cbls
        )
        
        cft_breakdown = [
            ComponentBreakdown(name="CCS (Comercialización)", value=ccs),
            ComponentBreakdown(name="CLUS (Limpieza Urbana)", value=clus),
            ComponentBreakdown(name="CBLS (Barrido y Limpieza)", value=cbls),
        ]
        
        # ========================================
        # 2. CALCULAR COMPONENTES VARIABLES (CVNA)
        # ========================================
        
        # CRT - Recolección y Transporte
        crt = self.calculator.calculate_crt(
            function=input_data.crt_function,
            distance_km=input_data.distance_km,
            avg_tons=input_data.avg_tons_collected,
            unpaved_road_km=input_data.unpaved_roads_km,
            is_coastal=input_data.is_coastal,
            fleet_age_years=input_data.fleet_age_years,
            tolls=input_data.tolls_per_ton
        )
        
        crt_details = {
            "function": "f1 (directo)" if input_data.crt_function == "f1" else "f2 (transferencia)",
            "distance_km": input_data.distance_km,
            "tons_collected": input_data.avg_tons_collected,
            "unpaved_roads_km": input_data.unpaved_roads_km,
            "is_coastal": input_data.is_coastal,
            "coastal_adjustment": "+1.97%" if input_data.is_coastal else "0%",
            "fleet_age_discount": f"-{input_data.fleet_age_years * 2}%" if input_data.fleet_age_years > 0 else "0%",
            "value": crt
        }
        
        # CDF - Disposición Final
        cdf = self.calculator.calculate_cdf(
            avg_tons=input_data.avg_tons_landfill,
            is_small_landfill=input_data.is_small_landfill
        )
        
        cdf_details = {
            "tons_landfill": input_data.avg_tons_landfill,
            "is_small_landfill": input_data.is_small_landfill,
            "value": cdf
        }
        
        # CTL - Tratamiento Lixiviados
        ctl = self.calculator.calculate_ctl(
            scenario=input_data.ctl_scenario,
            volume_m3=input_data.leachate_volume_m3
        )
        
        ctl_details = {
            "scenario": input_data.ctl_scenario,
            "volume_m3": input_data.leachate_volume_m3,
            "description": f"Escenario {input_data.ctl_scenario} de 5",
            "value": ctl
        }
        
        # CVNA = CRT + CDF + CTL
        cvna = self.calculator.calculate_cvna(
            crt=crt,
            cdf=cdf,
            ctl=ctl
        )
        
        # ========================================
        # 3. VALOR BASE APROVECHAMIENTO (VBA)
        # ========================================
        
        vba = self.calculator.calculate_vba(
            segment=input_data.segment
        )
        
        # ========================================
        # 4. TONELADAS POR SUSCRIPTOR
        # ========================================
        
        tons_non_recyclable = (
            input_data.tons_per_subscriber_sweep +
            input_data.tons_per_subscriber_urban +
            input_data.tons_per_subscriber_rejected +
            input_data.tons_per_subscriber_non_recoverable
        )
        
        tons_recyclable = input_data.tons_per_subscriber_recycled
        
        # ========================================
        # 5. TARIFA FINAL
        # ========================================
        
        tariff_base, tariff_final = self.calculator.calculate_final_tariff(
            cft=cft,
            cvna=cvna,
            vba=vba,
            trbl=input_data.tons_per_subscriber_sweep,
            trlu=input_data.tons_per_subscriber_urban,
            trra=input_data.tons_per_subscriber_rejected,
            tra=input_data.tons_per_subscriber_recycled,
            trna=input_data.tons_per_subscriber_non_recoverable,
            subsidy_contribution_factor=input_data.subsidy_contribution_factor
        )
        
        # ========================================
        # 6. NOTAS Y AJUSTES APLICADOS
        # ========================================
        
        formula_notes = [
            f"Resolución CRA 720 de 2015",
            f"Segmento {input_data.segment}",
            f"Tipo de facturación: {input_data.billing_type}",
            f"Con{'/' if input_data.has_recycling else 'sin'} aprovechamiento",
        ]
        
        applied_adjustments = []
        if input_data.is_coastal:
            applied_adjustments.append(f"Ajuste municipio costero: +1.97%")
        if input_data.unpaved_roads_km > 0:
            applied_adjustments.append(f"Vías sin pavimentar: +25% ({input_data.unpaved_roads_km} km)")
        if input_data.fleet_age_years > 0:
            applied_adjustments.append(f"Antigüedad flota: -{input_data.fleet_age_years * 2}% ({input_data.fleet_age_years} años)")
        if input_data.subsidy_contribution_factor != 0:
            pct = input_data.subsidy_contribution_factor * 100
            tipo = "Subsidio" if input_data.subsidy_contribution_factor < 0 else "Contribución"
            applied_adjustments.append(f"{tipo}: {pct:+.2f}%")
        
        # ========================================
        # 7. CONSTRUIR RESULTADO
        # ========================================
        
        result = TariffCalculationResult(
            # CFT
            ccs=ccs,
            clus=clus,
            cbls=cbls,
            cft=cft,
            cft_breakdown=cft_breakdown,
            
            # CVNA
            crt=crt,
            crt_details=crt_details,
            cdf=cdf,
            cdf_details=cdf_details,
            ctl=ctl,
            ctl_details=ctl_details,
            cvna=cvna,
            
            # VBA
            vba=vba,
            
            # Toneladas
            total_tons_non_recyclable=round(tons_non_recyclable, 4),
            total_tons_recyclable=round(tons_recyclable, 4),
            
            # Tarifa
            tariff_base=tariff_base,
            subsidy_contribution=round(tariff_final - tariff_base, 2),
            tariff_final=tariff_final,
            
            # Auditoría
            formula_notes=formula_notes,
            applied_adjustments=applied_adjustments if applied_adjustments else ["Ningún ajuste aplicado"]
        )
        
        return result
    
    def create_monthly_tariff(
        self,
        aps_id: int,
        period: str,
        input_data: TariffCalculationInput,
        current_user: User,
        notes: Optional[str] = None,
        calculation_type: str = "official"
    ) -> TariffCalculation:
        """
        Calcula tarifa y guarda en BD como tarifa oficial mensual
        
        Args:
            aps_id: ID del APS
            period: Período "2026-01"
            input_data: Parámetros de cálculo
            current_user: Usuario creando la tarifa (para auditoría)
            notes: Notas adicionales
            calculation_type: "official", "simulation", "test"
            
        Returns:
            TariffCalculation: Tarifa creada y guardada en BD
        """
        
        # Primero calcular
        result = self.calculate_tariff(input_data, current_user)
        
        # Crear modelo para guardar
        tariff_record = TariffCalculation(
            aps_id=aps_id,
            company_id=current_user.company_id,  # Del usuario
            period=period,
            calculation_type=calculation_type,
            calculated_by=current_user.id,
            calculation_date=datetime.utcnow(),
            
            # CFT
            cft=result.cft,
            ccs=result.ccs,
            clus=result.clus,
            cbls=result.cbls,
            clus_breakdown={},
            
            # CVNA
            cvna=result.cvna,
            crt=result.crt,
            cdf=result.cdf,
            ctl=result.ctl,
            crt_function_used=input_data.crt_function,
            crt_distance_km=input_data.distance_km,
            crt_avg_tons=input_data.avg_tons_collected,
            crt_tolls=input_data.tolls_per_ton,
            crt_coastal_adjustment=input_data.is_coastal,
            crt_fleet_age_discount=input_data.fleet_age_years * 2,
            
            cdf_vu=0.0,
            cdf_pc=0.0,
            cdf_avg_tons_landfill=input_data.avg_tons_landfill,
            cdf_adjustment_small_landfill=10.0 if input_data.is_small_landfill else 0.0,
            
            ctl_scenario=input_data.ctl_scenario,
            ctl_volume_m3=input_data.leachate_volume_m3,
            ctl_environmental_tax=0.0,
            ctl_vu=0.0,
            ctl_pc=0.0,
            
            # VBA
            vba=result.vba,
            vba_incentive_discount=0.0,
            
            # Toneladas
            trbl=input_data.tons_per_subscriber_sweep,
            trlu=input_data.tons_per_subscriber_urban,
            trra=input_data.tons_per_subscriber_rejected,
            tra=input_data.tons_per_subscriber_recycled,
            trna_stratum_1=input_data.tons_per_subscriber_non_recoverable,
            
            # Tarifa
            tariff_base=result.tariff_base,
            tariff_final=result.tariff_final,
            subsidy_contribution_factor=input_data.subsidy_contribution_factor,
            
            # Notas
            notes=notes or ""
        )
        
        # Guardar
        self.session.add(tariff_record)
        self.session.commit()
        self.session.refresh(tariff_record)
        
        return tariff_record
        """
        Calcula la tarifa oficial para un APS en un período
        
        Args:
            aps_id: ID del APS
            period: Período en formato YYYY-MM
            calculated_by: ID del usuario que realiza el cálculo
            subsidy_factors: Factores de subsidio/contribución personalizados
            
        Returns:
            TariffCalculation con resultado completo
        """
        return self._calculate_tariff(
            aps_id=aps_id,
            period=period,
            calculated_by=calculated_by,
            calculation_type="official",
            is_simulation=False,
            simulation_data=None,
            subsidy_factors=subsidy_factors
        )
    
    def calculate_simulation(
        self,
        aps_id: int,
        period: str,
        calculated_by: int,
        simulation_name: str,
        simulation_data: Dict,
        subsidy_factors: Optional[Dict[str, float]] = None
    ) -> TariffCalculation:
        """
        Calcula una simulación (sin guardar como oficial)
        
        Args:
            aps_id: ID del APS
            period: Período en formato YYYY-MM
            calculated_by: ID del usuario
            simulation_name: Nombre de la simulación
            simulation_data: Datos a sobrescribir para la simulación
            subsidy_factors: Factores personalizados
            
        Returns:
            TariffCalculation (marcado como simulación)
        """
        return self._calculate_tariff(
            aps_id=aps_id,
            period=period,
            calculated_by=calculated_by,
            calculation_type="simulation",
            is_simulation=True,
            simulation_name=simulation_name,
            simulation_data=simulation_data,
            subsidy_factors=subsidy_factors
        )
    
    def _calculate_tariff(
        self,
        aps_id: int,
        period: str,
        calculated_by: int,
        calculation_type: str,
        is_simulation: bool,
        simulation_name: Optional[str] = None,
        simulation_data: Optional[Dict] = None,
        subsidy_factors: Optional[Dict[str, float]] = None
    ) -> TariffCalculation:
        """Lógica interna de cálculo"""
        
        # 1. Obtener APS
        aps = self.aps_repo.get_by_id(aps_id)
        if not aps:
            raise ValueError(f"APS {aps_id} no encontrado")
        
        # 2. Obtener promedios de 6 meses
        averages = self.monthly_repo.calculate_6_month_averages(aps_id, period)
        if not averages:
            raise ValueError(f"No hay suficientes datos para calcular promedios en {period}")
        
        # 3. Sobrescribir con datos de simulación si aplica
        if simulation_data:
            averages.update(simulation_data)
        
        # 4. Determinar si hay aprovechamiento
        has_recycling = averages.get("tons_collected_recyclable", 0) > 0
        
        # 5. Calcular componentes
        
        # CCS - Comercialización
        ccs = self.calculator.calculate_ccs(
            segment=aps.segment,
            billing_type=aps.billing_type,
            has_recycling=has_recycling
        )
        
        # CLUS - Limpieza Urbana
        clus, clus_breakdown = self.calculator.calculate_clus(
            num_subscribers=int(averages["num_subscribers_total"]),
            tree_pruning_cost=averages.get("cost_tree_pruning", 0),
            grass_area_m2=averages.get("grass_area_cut_m2", 0),
            washing_area_m2=averages.get("public_areas_washed_m2", 0),
            beach_area_m2=averages.get("beach_cleaning_m2", 0),
            baskets_installed=averages.get("baskets_installed", 0),
            baskets_maintained=averages.get("baskets_maintained", 0),
            segment=aps.segment,
            water_price_per_m3=0  # TODO: Obtener precio del agua
        )
        
        # CBLS - Barrido y Limpieza
        cbls = self.calculator.calculate_cbls(
            sweeping_km=averages.get("sweeping_length_km", 0),
            num_subscribers=int(averages["num_subscribers_total"]),
            has_public_contribution=False  # TODO: Determinar si hay aporte
        )
        
        # CFT - Costo Fijo Total
        cft = self.calculator.calculate_cft(ccs, clus, cbls)
        
        # CRT - Recolección y Transporte
        crt, crt_details = self.calculator.calculate_crt(
            distance_km=aps.get_effective_distance(),
            avg_tons_month=averages["tons_collected_non_recyclable"],
            tolls_cost_month=0,  # TODO: Obtener peajes
            is_coastal=aps.is_coastal_municipality,
            uses_transfer_station=aps.uses_transfer_station,
            transfer_distance_km=aps.transfer_station_distance_km or 0,
            fleet_age_years=averages.get("fleet_average_age_years", 0),
            fleet_daily_shifts=averages.get("fleet_daily_shifts", 1),
            has_public_contribution=False  # TODO: Determinar si hay aporte
        )
        
        # CDF - Disposición Final
        cdf, cdf_details = self.calculator.calculate_cdf(
            avg_tons_landfill_month=averages["tons_received_landfill"],
            is_small_landfill=(averages["tons_received_landfill"] < 2400),
            extended_postclosure_years=0,  # TODO: Obtener de configuración
            has_public_contribution=False  # TODO: Determinar si hay aporte
        )
        
        # CTL - Tratamiento Lixiviados
        ctl, ctl_details = self.calculator.calculate_ctl(
            leachate_volume_m3=averages["leachate_volume_m3"],
            avg_tons_landfill_month=averages["tons_received_landfill"],
            scenario=averages.get("leachate_treatment_scenario", 2),
            environmental_tax=averages.get("environmental_tax_rate", 0),
            extended_postclosure_years=0,
            has_public_contribution=False
        )
        
        # CVNA - Costo Variable
        cvna = self.calculator.calculate_cvna(crt, cdf, ctl)
        
        # VBA - Aprovechamiento
        vba = self.calculator.calculate_vba(
            crt_avg=crt,  # Simplificado, debería ser promedio ponderado del municipio
            cdf_avg=cdf,
            incentive_discount=0.0  # TODO: Implementar DINC
        )
        
        # Toneladas comunes por suscriptor
        common_tons = self.calculator.calculate_tons_per_subscriber_common(
            tons_sweeping_month=averages["tons_collected_sweeping"],
            tons_urban_cleaning_month=averages["tons_collected_urban_cleaning"],
            tons_rejection_month=averages["tons_rejection_recycling"],
            tons_recycled_month=averages["tons_collected_recyclable"],
            num_subscribers_total=int(averages["num_subscribers_total"]),
            num_subscribers_vacant=int(averages["num_subscribers_vacant"]),
            num_subscribers_large_producers=averages.get("num_subscribers_large_producers", 0)
        )
        
        # TODO: Obtener distribución de suscriptores por estrato del monthly_data
        subscribers_by_stratum = {
            "stratum_1": averages.get("subscribers_stratum_1", 0),
            "stratum_2": averages.get("subscribers_stratum_2", 0),
            "stratum_3": averages.get("subscribers_stratum_3", 0),
            "stratum_4": averages.get("subscribers_stratum_4", 0),
            "stratum_5": averages.get("subscribers_stratum_5", 0),
            "stratum_6": averages.get("subscribers_stratum_6", 0),
            "commercial": averages.get("subscribers_commercial", 0),
        }
        
        # TRNA por estrato
        trna_by_stratum = self.calculator.calculate_trna_by_stratum(
            tons_non_recyclable_aps=averages["tons_collected_non_recyclable"],
            tons_rejection=averages["tons_rejection_recycling"],
            subscribers_by_stratum=subscribers_by_stratum,
            num_subscribers_vacant=int(averages["num_subscribers_vacant"]),
            tons_weighed_total=0  # TODO: Sumar toneladas aforadas
        )
        
        # Factores de subsidio/contribución por defecto
        if not subsidy_factors:
            subsidy_factors = {
                "stratum_1": -0.70,  # 70% subsidio
                "stratum_2": -0.40,  # 40% subsidio
                "stratum_3": -0.15,  # 15% subsidio
                "stratum_4": 0.00,   # Sin subsidio ni contribución
                "stratum_5": 0.20,   # 20% contribución
                "stratum_6": 0.20,   # 20% contribución
                "commercial": 0.30   # 30% contribución
            }
        
        # Calcular tarifas finales por estrato
        tariffs = {}
        for stratum in ["stratum_1", "stratum_2", "stratum_3", "stratum_4", 
                       "stratum_5", "stratum_6", "commercial"]:
            base, final = self.calculator.calculate_final_tariff(
                cft=cft,
                cvna=cvna,
                vba=vba,
                trbl=common_tons["trbl"],
                trlu=common_tons["trlu"],
                trra=common_tons["trra"],
                tra=common_tons["tra"],
                trna=trna_by_stratum[stratum],
                subsidy_contribution_factor=subsidy_factors[stratum]
            )
            tariffs[stratum] = {"base": base, "final": final}
        
        # Crear registro de cálculo
        calculation = TariffCalculation(
            company_id=aps.company_id,
            aps_id=aps_id,
            calculation_type=calculation_type,
            period=period,
            calculated_by=calculated_by,
            calculation_date=datetime.utcnow(),
            
            # Costos
            cft=cft,
            ccs=ccs,
            clus=clus,
            cbls=cbls,
            clus_breakdown=clus_breakdown,
            
            cvna=cvna,
            crt=crt,
            cdf=cdf,
            ctl=ctl,
            
            # Detalles CRT
            crt_function_used=crt_details["function_used"],
            crt_distance_km=aps.get_effective_distance(),
            crt_avg_tons=averages["tons_collected_non_recyclable"],
            crt_tolls=crt_details.get("tolls_per_ton", 0),
            crt_coastal_adjustment=crt_details.get("coastal_adjustment", False),
            crt_fleet_age_discount=crt_details.get("fleet_age_discount", 0),
            
            # Detalles CDF
            cdf_vu=cdf_details["cdf_vu"],
            cdf_pc=cdf_details["cdf_pc"],
            cdf_avg_tons_landfill=averages["tons_received_landfill"],
            
            # Detalles CTL
            ctl_scenario=averages.get("leachate_treatment_scenario", 2),
            ctl_volume_m3=averages["leachate_volume_m3"],
            ctl_environmental_tax=averages.get("environmental_tax_rate", 0),
            ctl_vu=ctl_details["ctlm_vu"],
            ctl_pc=ctl_details["ctlm_pc"],
            
            # Aprovechamiento
            vba=vba,
            vba_incentive_discount=0.0,
            
            # Toneladas
            trbl=common_tons["trbl"],
            trlu=common_tons["trlu"],
            trra=common_tons["trra"],
            tra=common_tons["tra"],
            
            trna_stratum_1=trna_by_stratum["stratum_1"],
            trna_stratum_2=trna_by_stratum["stratum_2"],
            trna_stratum_3=trna_by_stratum["stratum_3"],
            trna_stratum_4=trna_by_stratum["stratum_4"],
            trna_stratum_5=trna_by_stratum["stratum_5"],
            trna_stratum_6=trna_by_stratum["stratum_6"],
            trna_commercial=trna_by_stratum["commercial"],
            
            # Tarifas
            tariff_stratum_1_base=tariffs["stratum_1"]["base"],
            tariff_stratum_2_base=tariffs["stratum_2"]["base"],
            tariff_stratum_3_base=tariffs["stratum_3"]["base"],
            tariff_stratum_4_base=tariffs["stratum_4"]["base"],
            tariff_stratum_5_base=tariffs["stratum_5"]["base"],
            tariff_stratum_6_base=tariffs["stratum_6"]["base"],
            tariff_commercial_base=tariffs["commercial"]["base"],
            
            tariff_stratum_1_final=tariffs["stratum_1"]["final"],
            tariff_stratum_2_final=tariffs["stratum_2"]["final"],
            tariff_stratum_3_final=tariffs["stratum_3"]["final"],
            tariff_stratum_4_final=tariffs["stratum_4"]["final"],
            tariff_stratum_5_final=tariffs["stratum_5"]["final"],
            tariff_stratum_6_final=tariffs["stratum_6"]["final"],
            tariff_commercial_final=tariffs["commercial"]["final"],
            
            # Subsidios
            subsidy_contribution_factors=subsidy_factors,
            
            # Snapshot de datos
            input_data=averages,
            
            # Fórmulas usadas
            formulas_used=self._get_formulas_used(),
            regulatory_references=self._get_regulatory_references(),
            
            # Validaciones
            validations=self._validate_calculation(aps, averages, tariffs),
            
            # Metadatos
            is_simulation=is_simulation,
            simulation_name=simulation_name
        )
        
        # Guardar en base de datos
        self.session.add(calculation)
        self.session.commit()
        self.session.refresh(calculation)
        
        return calculation
    
    def _get_formulas_used(self) -> Dict:
        """Retorna las fórmulas usadas con referencias"""
        return {
            "CFT": "CFT = CCS + CLUS + CBLS",
            "CVNA": "CVNA = CRT + CDF + CTL",
            "CRT": "CRT = MIN(f1, f2) + PRT",
            "CDF": "CDF = CDF_VU + CDF_PC",
            "CTL": "CTL = ((CTLM × VL) + CMTLX) / QRS",
            "VBA": "VBA = (CRT_p + CDF_p) × (1 - DINC)",
            "TFS": "TFS = (CFT + CVNA × (TRBL + TRLU + TRNA + TRRA) + (VBA × TRA)) × (1 ± FCS)"
        }
    
    def _get_regulatory_references(self) -> Dict:
        """Retorna las referencias a artículos de la Resolución 720"""
        return {
            "CFT": ["Art. 11"],
            "CCS": ["Art. 14"],
            "CLUS": ["Art. 15-20"],
            "CBLS": ["Art. 21-23"],
            "CRT": ["Art. 24-27"],
            "CDF": ["Art. 28-31"],
            "CTL": ["Art. 32-33", "Anexo II"],
            "VBA": ["Art. 34-35"],
            "TFS": ["Art. 39"]
        }
    
    def _validate_calculation(
        self, 
        aps: APS, 
        averages: Dict, 
        tariffs: Dict
    ) -> Dict:
        """Valida el cálculo y genera alertas"""
        validations = {
            "min_frequency_met": True,  # TODO: Validar frecuencia mínima
            "compaction_density_ok": True,  # TODO: Validar densidad
            "within_max_costs": True,  # TODO: Validar costos máximos
            "alerts": []
        }
        
        # Alerta: Distancia > 50 km
        if aps.get_effective_distance() > 50:
            validations["alerts"].append(
                "Distancia >50km: considerar estación de transferencia (Art. 24)"
            )
        
        # Alerta: Relleno pequeño
        if averages["tons_received_landfill"] < 2400:
            validations["alerts"].append(
                "Relleno <2,400 ton/mes: aplica ajuste Art. 28 Parágrafo 2"
            )
        
        # Alerta: Flota antigua
        if averages.get("fleet_average_age_years", 0) > 12:
            validations["alerts"].append(
                "Flota >12 años: descuento aplicado por antigüedad (Art. 27)"
            )
        
        return validations
