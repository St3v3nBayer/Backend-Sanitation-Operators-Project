from typing import List, Optional
from sqlmodel import Session, select
from app.models.aps import APS
from app.models.aps_monthly_data import APSMonthlyData


class APSRepository:
    """Repositorio para operaciones con APS"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # ========================================
    # OPERACIONES CRUD BÁSICAS
    # ========================================
    
    def create(self, aps: APS) -> APS:
        """Crea un nuevo APS"""
        self.session.add(aps)
        self.session.commit()
        self.session.refresh(aps)
        return aps
    
    def get_by_id(self, aps_id: int) -> Optional[APS]:
        """Obtiene un APS por ID"""
        return self.session.get(APS, aps_id)
    
    def get_by_code(self, code: str) -> Optional[APS]:
        """Obtiene un APS por su código único"""
        statement = select(APS).where(APS.code == code)
        return self.session.exec(statement).first()
    
    def get_all_by_company(
        self, 
        company_id: int, 
        only_active: bool = True
    ) -> List[APS]:
        """Obtiene todos los APS de una empresa"""
        statement = select(APS).where(APS.company_id == company_id)
        if only_active:
            statement = statement.where(APS.is_active == True)
        return list(self.session.exec(statement).all())
    
    def update(self, aps_id: int, data: dict) -> Optional[APS]:
        """Actualiza un APS"""
        aps = self.get_by_id(aps_id)
        if not aps:
            return None
        
        for key, value in data.items():
            if hasattr(aps, key) and value is not None:
                setattr(aps, key, value)
        
        self.session.add(aps)
        self.session.commit()
        self.session.refresh(aps)
        return aps
    
    def delete(self, aps_id: int) -> bool:
        """Elimina (desactiva) un APS"""
        aps = self.get_by_id(aps_id)
        if not aps:
            return False
        
        aps.is_active = False
        self.session.add(aps)
        self.session.commit()
        return True
    
    # ========================================
    # CONSULTAS ESPECÍFICAS
    # ========================================
    
    def get_by_municipality(
        self, 
        municipality: str, 
        department: str
    ) -> List[APS]:
        """Obtiene todos los APS de un municipio"""
        statement = select(APS).where(
            APS.municipality == municipality,
            APS.department == department,
            APS.is_active == True
        )
        return list(self.session.exec(statement).all())
    
    def get_coastal_aps(self) -> List[APS]:
        """Obtiene todos los APS en municipios costeros"""
        statement = select(APS).where(
            APS.is_coastal_municipality == True,
            APS.is_active == True
        )
        return list(self.session.exec(statement).all())
    
    def get_aps_with_transfer_station(self) -> List[APS]:
        """Obtiene APS que usan estación de transferencia"""
        statement = select(APS).where(
            APS.uses_transfer_station == True,
            APS.is_active == True
        )
        return list(self.session.exec(statement).all())


class APSMonthlyDataRepository:
    """Repositorio para datos mensuales del APS"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, data: APSMonthlyData) -> APSMonthlyData:
        """Crea un registro mensual"""
        # Extraer año y mes del período
        year, month = map(int, data.period.split('-'))
        data.year = year
        data.month = month
        
        # Convertir áreas de playa a kilómetros
        if data.beach_cleaning_m2 > 0:
            data.beach_cleaning_km = data.beach_cleaning_m2 * 0.0007
        
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def get_by_id(self, data_id: int) -> Optional[APSMonthlyData]:
        """Obtiene datos mensuales por ID"""
        return self.session.get(APSMonthlyData, data_id)
    
    def get_by_aps_and_period(
        self, 
        aps_id: int, 
        period: str
    ) -> Optional[APSMonthlyData]:
        """Obtiene datos de un APS en un período específico"""
        statement = select(APSMonthlyData).where(
            APSMonthlyData.aps_id == aps_id,
            APSMonthlyData.period == period
        )
        return self.session.exec(statement).first()
    
    def get_last_6_months(self, aps_id: int, end_period: str) -> List[APSMonthlyData]:
        """
        Obtiene los datos de los últimos 6 meses para un APS
        
        Necesario para calcular promedios según Art. 4 de Resolución 720
        """
        year, month = map(int, end_period.split('-'))
        
        # Calcular 6 meses hacia atrás
        periods = []
        for i in range(6):
            m = month - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            periods.append(f"{y:04d}-{m:02d}")
        
        statement = select(APSMonthlyData).where(
            APSMonthlyData.aps_id == aps_id,
            APSMonthlyData.period.in_(periods)
        ).order_by(APSMonthlyData.year.desc(), APSMonthlyData.month.desc())
        
        return list(self.session.exec(statement).all())
    
    def get_all_by_aps(
        self, 
        aps_id: int, 
        year: Optional[int] = None
    ) -> List[APSMonthlyData]:
        """Obtiene todos los datos mensuales de un APS"""
        statement = select(APSMonthlyData).where(APSMonthlyData.aps_id == aps_id)
        
        if year:
            statement = statement.where(APSMonthlyData.year == year)
        
        statement = statement.order_by(
            APSMonthlyData.year.desc(), 
            APSMonthlyData.month.desc()
        )
        
        return list(self.session.exec(statement).all())
    
    def update(self, data_id: int, updates: dict) -> Optional[APSMonthlyData]:
        """Actualiza datos mensuales"""
        data = self.get_by_id(data_id)
        if not data:
            return None
        
        for key, value in updates.items():
            if hasattr(data, key) and value is not None:
                setattr(data, key, value)
        
        # Re-calcular conversiones si es necesario
        if 'beach_cleaning_m2' in updates:
            data.beach_cleaning_km = data.beach_cleaning_m2 * 0.0007
        
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def verify_data(
        self, 
        data_id: int, 
        verified_by: int
    ) -> Optional[APSMonthlyData]:
        """Marca datos como verificados por un auditor"""
        from datetime import datetime
        
        data = self.get_by_id(data_id)
        if not data:
            return None
        
        data.verified = True
        data.verified_by = verified_by
        data.verified_at = datetime.utcnow()
        
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def calculate_6_month_averages(
        self, 
        aps_id: int, 
        end_period: str
    ) -> dict:
        """
        Calcula los promedios de 6 meses según Art. 4
        
        Returns:
            dict con promedios de todas las variables operativas
        """
        data_list = self.get_last_6_months(aps_id, end_period)
        
        if not data_list:
            return {}
        
        # Inicializar sumas
        totals = {
            "num_subscribers_total": 0,
            "num_subscribers_vacant": 0,
            "tons_collected_non_recyclable": 0.0,
            "tons_collected_sweeping": 0.0,
            "tons_collected_urban_cleaning": 0.0,
            "tons_collected_recyclable": 0.0,
            "tons_rejection_recycling": 0.0,
            "tons_received_landfill": 0.0,
            "leachate_volume_m3": 0.0,
            "sweeping_length_km": 0.0,
        }
        
        count = len(data_list)
        
        # Sumar todos los valores
        for data in data_list:
            for key in totals.keys():
                totals[key] += getattr(data, key, 0) or 0
        
        # Calcular promedios
        averages = {key: value / count for key, value in totals.items()}
        averages["months_count"] = count
        
        return averages
