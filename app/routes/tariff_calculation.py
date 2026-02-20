"""
Routes para Cálculo y Validación de Tarifas según Resolución 720
Endpoints para:
1. Validador: Simular tarifas (para validar fórmula)
2. Creador: Crear tarifas mensuales (guardar en BD)
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..schemas.tariff_calculation import (
    SimulateTariffRequest,
    TariffCalculationResult,
    CreateTariffRequest,
    TariffHistoryResponse,
    TariffHistoryItem,
)
from ..services.tariff_calculation_service import TariffCalculationService
from ..models.user import User
from ..models.tariff_calculation import TariffCalculation
from ..core.deps import get_current_user, get_session
from ..core.validators import (
    validate_period_format,
    validate_user_owns_aps,
    validate_tariff_not_exists,
    validate_tariff_calculation_input,
)
from ..core.exceptions import UnauthorizedError


router = APIRouter(prefix="/api/tariff-calculation", tags=["tariff-calculation"])


@router.post("/validator/simulate", response_model=TariffCalculationResult)
async def simulate_tariff(
    request: SimulateTariffRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TariffCalculationResult:
    """
    Simula un cálculo de tarifa SIN guardar en BD
    
    Usado para:
    - Validar que la fórmula da los mismos resultados que datos históricos
    - Explorar escenarios diferentes
    - Educar al tarifador sobre cómo funciona Res 720
    
    **Ejemplo: Validar tarifa de enero 2025**
    ```
    1. Tarifador carga en Excel: datos de enero 2025
    2. Los carga en simulador
    3. Compara resultado vs su histórico
    4. "Exactamente igual" ✓
    5. Ahora confía que fórmula está correcta
    ```
    """
    
    if not current_user:
        raise UnauthorizedError()
    
    # Validar datos de entrada
    validate_tariff_calculation_input(request.input_data.dict())
    
    service = TariffCalculationService(session)
    result = service.calculate_tariff(
        input_data=request.input_data,
        current_user=current_user
    )
    
    return result


@router.post("/monthly/create", response_model=dict)
async def create_monthly_tariff(
    request: CreateTariffRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> dict:
    """
    Crea tarifa mensual oficial para un APS
    
    **Guarda en BD** para histórico y auditoría
    
    Usado para:
    - Crear tarifa oficial de enero 2026
    - Crear tarifa oficial de febrero 2026
    - Etc., mes a mes
    
    **Flujo:**
    ```
    Enero 2026:
    └─ Tarifador llena datos de enero
    └─ Sistema calcula
    └─ Guarda como tarifa oficial
    
    Febrero 2026:
    └─ Tarifador llena datos de febrero
    └─ Sistema calcula
    └─ Guarda como tarifa oficial (diferente a enero)
    
    Histórico:
    └─ 12 tarifas guardadas en BD (ene-dic 2026)
    ```
    """
    
    if not current_user:
        raise UnauthorizedError()
    
    # Validaciones centralizadas
    validate_period_format(request.period)
    aps = validate_user_owns_aps(session, request.aps_id, current_user)
    validate_tariff_not_exists(session, request.aps_id, request.period)
    validate_tariff_calculation_input(request.input_data.dict())
    
    service = TariffCalculationService(session)
    
    tariff_record = service.create_monthly_tariff(
        aps_id=request.aps_id,
        period=request.period,
        input_data=request.input_data,
        current_user=current_user,
        notes=request.notes,
        calculation_type=request.calculation_type
    )
    
    return {
        "id": tariff_record.id,
        "aps_id": tariff_record.aps_id,
        "period": tariff_record.period,
        "tariff_final": tariff_record.tariff_final,
        "tariff_base": tariff_record.tariff_base,
        "calculated_by": tariff_record.calculated_by,
        "calculation_date": tariff_record.calculation_date,
        "message": f"Tarifa creada para {aps.name} en período {request.period}"
    }


@router.get("/aps/{aps_id}/history", response_model=TariffHistoryResponse)
async def get_tariff_history(
    aps_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TariffHistoryResponse:
    """
    Obtiene histórico de tarifas de un APS
    
    Útil para ver tendencias y detectar anomalías
    """
    
    if not current_user:
        raise UnauthorizedError()
    
    # Validar que APS existe y pertenece al usuario
    aps = validate_user_owns_aps(session, aps_id, current_user)
    
    tariffs = session.exec(
        select(TariffCalculation)
        .where(TariffCalculation.aps_id == aps_id)
        .order_by(TariffCalculation.period.desc())
    ).all()
    
    history_items = [
        TariffHistoryItem(
            id=t.id,
            period=t.period,
            tariff_final=t.tariff_final,
            calculated_by=t.calculated_by,
            calculation_date=t.calculation_date,
            calculation_type=t.calculation_type,
            notes=getattr(t, 'notes', None)
        )
        for t in tariffs
    ]
    
    return TariffHistoryResponse(
        aps_id=aps_id,
        total_count=len(history_items),
        tariffs=history_items
    )


@router.get("/period/{period}/aps-detail", response_model=dict)
async def get_tariff_detail(
    period: str,
    aps_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> dict:
    """
    Obtiene detalles completos de una tarifa calculada
    """
    
    if not current_user:
        raise UnauthorizedError()
    
    # Validar período format y que APS existe
    validate_period_format(period)
    aps = validate_user_owns_aps(session, aps_id, current_user)
    
    tariff = session.exec(
        select(TariffCalculation).where(
            (TariffCalculation.aps_id == aps_id) &
            (TariffCalculation.period == period)
        )
    ).first()
    
    if not tariff:
        from ..core.exceptions import TariffNotFoundError
        raise TariffNotFoundError(aps_id)
    
    user = session.exec(
        select(User).where(User.id == tariff.calculated_by)
    ).first()
    
    return {
        "period": tariff.period,
        "aps_id": tariff.aps_id,
        "aps_name": aps.name,
        "cft": tariff.cft,
        "ccs": tariff.ccs,
        "clus": tariff.clus,
        "cbls": tariff.cbls,
        "cvna": tariff.cvna,
        "crt": tariff.crt,
        "cdf": tariff.cdf,
        "ctl": tariff.ctl,
        "vba": tariff.vba,
        "tariff_base": tariff.tariff_base,
        "tariff_final": tariff.tariff_final,
        "calculation_type": tariff.calculation_type,
        "calculated_date": tariff.calculation_date,
        "calculated_by_username": user.username if user else "unknown",
        "notes": getattr(tariff, 'notes', "")
    }
