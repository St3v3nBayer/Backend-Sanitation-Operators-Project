from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.deps import get_session, get_current_user, check_user_role
from app.controllers.aps_controller import APSController
from app.schemas.aps import (
    APSCreate, APSUpdate, APSRead,
    APSMonthlyDataCreate, APSMonthlyDataRead
)
from app.models.user import User

router = APIRouter(prefix="/aps", tags=["APS - Áreas de Prestación del Servicio"])


# ========================================
# ENDPOINTS CRUD APS
# ========================================

@router.post("/", response_model=APSRead, status_code=201)
def create_aps(
    data: APSCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo APS (Área de Prestación del Servicio)
    
    **Permisos**: SYSTEM, ADMIN
    
    - **SYSTEM**: Puede crear APS para cualquier empresa
    - **ADMIN**: Solo puede crear APS para su propia empresa
    
    El APS representa el área geográfica donde la empresa presta el servicio
    de recolección y transporte de residuos sólidos.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN"])
    controller = APSController(session)
    return controller.create_aps(
        data=data,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.get("/{aps_id}", response_model=APSRead)
def get_aps(
    aps_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un APS por ID
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    Los usuarios solo pueden ver APS de su propia empresa.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.get_aps(
        aps_id=aps_id,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.get("/company/{company_id}", response_model=List[APSRead])
def get_aps_by_company(
    company_id: int,
    only_active: bool = Query(True, description="Solo APS activos"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los APS de una empresa
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    Los usuarios solo pueden ver APS de su propia empresa.
    SYSTEM puede ver APS de cualquier empresa.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.get_all_aps_by_company(
        company_id=company_id,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM"),
        only_active=only_active
    )


@router.put("/{aps_id}", response_model=APSRead)
def update_aps(
    aps_id: int,
    data: APSUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un APS
    
    **Permisos**: SYSTEM, ADMIN
    
    Los ADMIN solo pueden actualizar APS de su propia empresa.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN"])
    controller = APSController(session)
    return controller.update_aps(
        aps_id=aps_id,
        data=data,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.delete("/{aps_id}")
def delete_aps(
    aps_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Desactiva un APS
    
    **Permisos**: SYSTEM, ADMIN
    
    No elimina físicamente, solo marca como inactivo.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN"])
    controller = APSController(session)
    return controller.delete_aps(
        aps_id=aps_id,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


# ========================================
# ENDPOINTS DATOS MENSUALES
# ========================================

@router.post("/{aps_id}/monthly-data", response_model=APSMonthlyDataRead, status_code=201)
def create_monthly_data(
    aps_id: int,
    data: APSMonthlyDataCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crea o actualiza datos mensuales para un APS
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    Registra los datos operativos del mes para el APS.
    Estos datos se usan para calcular los promedios de 6 meses
    según la Resolución CRA 720 de 2015, Artículo 4.
    
    Si ya existen datos para el período, los actualiza.
    """
    # Asegurar que el aps_id coincida
    data.aps_id = aps_id
    
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.create_monthly_data(
        data=data,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.get("/{aps_id}/monthly-data/{period}", response_model=APSMonthlyDataRead)
def get_monthly_data(
    aps_id: int,
    period: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene datos mensuales de un APS para un período específico
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    El período debe estar en formato YYYY-MM (ej: "2026-02")
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.get_monthly_data(
        aps_id=aps_id,
        period=period,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.get("/{aps_id}/monthly-data", response_model=List[APSMonthlyDataRead])
def get_all_monthly_data(
    aps_id: int,
    year: Optional[int] = Query(None, description="Filtrar por año"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los datos mensuales de un APS
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    Opcionalmente puede filtrar por año.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.get_all_monthly_data(
        aps_id=aps_id,
        year=year,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.get("/{aps_id}/averages/{end_period}")
def get_six_month_averages(
    aps_id: int,
    end_period: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Calcula los promedios de 6 meses para un APS
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    Según Resolución CRA 720 de 2015, Artículo 4:
    "Cuando en la presente resolución se determine que los cálculos 
    se realicen con el promedio de: kilómetros de barrido y limpieza, 
    toneladas de residuos, metros cúbicos de lixiviados y número de 
    suscriptores, se tomará el promedio mensual del semestre 
    inmediatamente anterior"
    
    El end_period debe estar en formato YYYY-MM (ej: "2026-02")
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.get_6_month_averages(
        aps_id=aps_id,
        end_period=end_period,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.put("/monthly-data/{data_id}/verify")
def verify_monthly_data(
    data_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Verifica datos mensuales (marca como verificados por auditor)
    
    **Permisos**: SYSTEM, ADMIN
    
    Usado para auditoría y control de calidad de datos.
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN"])
    controller = APSController(session)
    return controller.verify_monthly_data(
        data_id=data_id,
        verified_by_user_id=current_user.id,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


# ========================================
# ENDPOINTS CONSULTAS ESPECIALES
# ========================================

@router.get("/{aps_id}/summary")
def get_aps_summary(
    aps_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un resumen completo del APS
    
    **Permisos**: SYSTEM, ADMIN, USER
    
    Incluye:
    - Datos básicos del APS
    - Último mes registrado
    - Promedios de 6 meses
    - Distancia efectiva ajustada por vías sin pavimentar
    - Total de meses registrados
    """
    check_user_role(current_user, ["SYSTEM", "ADMIN", "USER"])
    controller = APSController(session)
    return controller.get_aps_summary(
        aps_id=aps_id,
        current_user_company_id=current_user.company_id,
        is_system_user=(current_user.role == "SYSTEM")
    )


@router.get("/municipality/{municipality}/{department}", response_model=List[APSRead])
def get_aps_by_municipality(
    municipality: str,
    department: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los APS de un municipio
    
    **Permisos**: Solo SYSTEM
    
    Útil para análisis regulatorios y comparaciones entre prestadores.
    """
    check_user_role(current_user, ["SYSTEM"])
    controller = APSController(session)
    return controller.get_aps_by_municipality(
        municipality=municipality,
        department=department,
        is_system_user=True
    )
