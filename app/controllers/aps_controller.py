from typing import List, Optional, Dict
from sqlmodel import Session
from datetime import datetime

from app.repositories.aps_repository import APSRepository, APSMonthlyDataRepository
from app.models.aps import APS
from app.models.aps_monthly_data import APSMonthlyData
from app.schemas.aps import (
    APSCreate, APSUpdate, APSRead,
    APSMonthlyDataCreate, APSMonthlyDataRead
)
from app.core.exceptions import (
    APSNotBelongsToCompanyError,
    APSNotFoundError,
    ValidationError,
    InsufficientPermissionsError,
)


class APSController:
    """Controlador para operaciones con APS"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repository = APSRepository(session)
        self.monthly_repo = APSMonthlyDataRepository(session)
    
    # ========================================
    # OPERACIONES CRUD
    # ========================================
    
    def create_aps(
        self, 
        data: APSCreate, 
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> APS:
        """
        Crea un nuevo APS
        
        Args:
            data: Datos del APS a crear
            current_user_company_id: ID de la empresa del usuario actual
            is_system_user: Si el usuario es SYSTEM (puede crear para cualquier empresa)
        """
        # Validar permisos
        if not is_system_user and data.company_id != current_user_company_id:
            raise APSNotBelongsToCompanyError(0, data.company_id)
        
        # Validar que el código sea único
        existing = self.repository.get_by_code(data.code)
        if existing:
            raise ValidationError("code", f"Ya existe un APS con el código '{data.code}'")
        
        # Crear APS
        aps = APS(**data.model_dump())
        aps.updated_at = datetime.utcnow()
        
        return self.repository.create(aps)
    
    def get_aps(
        self, 
        aps_id: int,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> APS:
        """Obtiene un APS por ID"""
        aps = self.repository.get_by_id(aps_id)
        
        if not aps:
            raise APSNotFoundError(aps_id)
        
        # Validar permisos
        if not is_system_user and aps.company_id != current_user_company_id:
            raise APSNotBelongsToCompanyError(aps_id, aps.company_id)
        
        return aps
    
    def get_all_aps_by_company(
        self,
        company_id: int,
        current_user_company_id: int,
        is_system_user: bool = False,
        only_active: bool = True
    ) -> List[APS]:
        """Obtiene todos los APS de una empresa"""
        # Validar permisos
        if not is_system_user and company_id != current_user_company_id:
            raise InsufficientPermissionsError("No tiene permisos para ver APS de otra empresa")
        
        return self.repository.get_all_by_company(company_id, only_active)
    
    def update_aps(
        self,
        aps_id: int,
        data: APSUpdate,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> APS:
        """Actualiza un APS"""
        aps = self.get_aps(aps_id, current_user_company_id, is_system_user)
        
        # Preparar datos para actualizar
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        updated_aps = self.repository.update(aps_id, update_data)
        
        if not updated_aps:
            raise ValidationError("aps", "Error al actualizar APS")
        
        return updated_aps
    
    def delete_aps(
        self,
        aps_id: int,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> dict:
        """Desactiva un APS"""
        aps = self.get_aps(aps_id, current_user_company_id, is_system_user)
        
        success = self.repository.delete(aps_id)
        
        if not success:
            raise ValidationError("aps", "Error al desactivar APS")
        
        return {"message": "APS desactivado exitosamente"}
    
    # ========================================
    # DATOS MENSUALES
    # ========================================
    
    def create_monthly_data(
        self,
        data: APSMonthlyDataCreate,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> APSMonthlyData:
        """Crea o actualiza datos mensuales para un APS"""
        # Validar que el APS existe y pertenece a la empresa
        aps = self.get_aps(data.aps_id, current_user_company_id, is_system_user)
        
        # Verificar si ya existen datos para este período
        existing = self.monthly_repo.get_by_aps_and_period(data.aps_id, data.period)
        
        if existing:
            # Actualizar datos existentes
            update_data = data.model_dump(exclude={"aps_id", "period"})
            updated = self.monthly_repo.update(existing.id, update_data)
            return updated
        
        # Crear nuevos datos
        monthly_data = APSMonthlyData(**data.model_dump())
        return self.monthly_repo.create(monthly_data)
    
    def get_monthly_data(
        self,
        aps_id: int,
        period: str,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> APSMonthlyData:
        """Obtiene datos mensuales de un APS"""
        # Validar permisos
        aps = self.get_aps(aps_id, current_user_company_id, is_system_user)
        
        data = self.monthly_repo.get_by_aps_and_period(aps_id, period)
        
        if not data:
            raise APSNotFoundError(aps_id)
        
        return data
    
    def get_all_monthly_data(
        self,
        aps_id: int,
        year: Optional[int] = None,
        current_user_company_id: int = None,
        is_system_user: bool = False
    ) -> List[APSMonthlyData]:
        """Obtiene todos los datos mensuales de un APS"""
        # Validar permisos
        aps = self.get_aps(aps_id, current_user_company_id, is_system_user)
        
        return self.monthly_repo.get_all_by_aps(aps_id, year)
    
    def get_6_month_averages(
        self,
        aps_id: int,
        end_period: str,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> Dict:
        """
        Calcula promedios de 6 meses según Art. 4 de Resolución 720
        
        Returns:
            Dict con promedios de todas las variables operativas
        """
        # Validar permisos
        aps = self.get_aps(aps_id, current_user_company_id, is_system_user)
        
        averages = self.monthly_repo.calculate_6_month_averages(aps_id, end_period)
        
        if not averages:
            raise ValidationError("aps", "No hay suficientes datos para calcular promedios de 6 meses")
        
        return averages
    
    def verify_monthly_data(
        self,
        data_id: int,
        verified_by_user_id: int,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> APSMonthlyData:
        """Marca datos mensuales como verificados por un auditor"""
        data = self.monthly_repo.get_by_id(data_id)
        
        if not data:
            raise APSNotFoundError(data_id)
        
        # Validar permisos
        aps = self.get_aps(data.aps_id, current_user_company_id, is_system_user)
        
        verified = self.monthly_repo.verify_data(data_id, verified_by_user_id)
        
        if not verified:
            raise ValidationError("aps", "Error al verificar datos")
        
        return verified
    
    # ========================================
    # CONSULTAS ESPECIALES
    # ========================================
    
    def get_aps_summary(
        self,
        aps_id: int,
        current_user_company_id: int,
        is_system_user: bool = False
    ) -> Dict:
        """
        Obtiene un resumen completo del APS incluyendo:
        - Datos básicos del APS
        - Último mes registrado
        - Promedios de 6 meses
        - Distancia efectiva ajustada
        """
        # Obtener APS
        aps = self.get_aps(aps_id, current_user_company_id, is_system_user)
        
        # Obtener último mes registrado
        all_data = self.monthly_repo.get_all_by_aps(aps_id)
        last_month = all_data[0] if all_data else None
        
        # Calcular promedios si hay datos
        averages = None
        if last_month:
            try:
                averages = self.monthly_repo.calculate_6_month_averages(
                    aps_id, 
                    last_month.period
                )
            except:
                averages = None
        
        return {
            "aps": aps,
            "last_month_data": last_month,
            "six_month_averages": averages,
            "effective_distance_km": aps.get_effective_distance(),
            "total_months_registered": len(all_data)
        }
    
    def get_aps_by_municipality(
        self,
        municipality: str,
        department: str,
        is_system_user: bool = False
    ) -> List[APS]:
        """Obtiene todos los APS de un municipio (solo para SYSTEM)"""
        if not is_system_user:
            raise InsufficientPermissionsError("Solo usuarios SYSTEM pueden consultar por municipio")
        
        return self.repository.get_by_municipality(municipality, department)
