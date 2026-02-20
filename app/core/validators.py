"""
Validaciones centralizadas de negocio
"""

import re
from datetime import datetime
from sqlmodel import Session, select

from .exceptions import (
    APSNotFoundError,
    APSAccessDeniedError,
    APSNotBelongsToCompanyError,
    InvalidPeriodError,
    TariffAlreadyExistsError,
    UnauthorizedError,
)
from ..models.aps import APS
from ..models.user import User
from ..models.tariff_calculation import TariffCalculation


def validate_period_format(period: str) -> str:
    """
    Valida que el período tenga formato YYYY-MM
    Returns: period si es válido
    Raises: InvalidPeriodError si no es válido
    """
    pattern = r'^\d{4}-\d{2}$'
    
    if not re.match(pattern, period):
        raise InvalidPeriodError(period)
    
    # Validar que año y mes sean válidos
    try:
        year, month = period.split('-')
        year = int(year)
        month = int(month)
        
        if not (1 <= month <= 12):
            raise InvalidPeriodError(period)
        
        if year < 2000 or year > 2099:
            raise InvalidPeriodError(period)
            
    except ValueError:
        raise InvalidPeriodError(period)
    
    return period


def validate_user_owns_aps(
    session: Session,
    aps_id: int,
    current_user: User
) -> APS:
    """
    Valida que:
    1. APS existe
    2. Usuario tiene acceso (pertenece a la misma empresa)
    
    Returns: APS object
    Raises: Excepciones si validación falla
    """
    
    if not current_user:
        raise UnauthorizedError()
    
    # Obtener APS
    statement = select(APS).where(APS.id == aps_id)
    aps = session.exec(statement).first()
    
    if not aps:
        raise APSNotFoundError(aps_id)
    
    # Validar que pertenece a la empresa del usuario
    if aps.company_id != current_user.company_id:
        raise APSNotBelongsToCompanyError(aps_id, current_user.company_id)
    
    return aps


def validate_tariff_not_exists(
    session: Session,
    aps_id: int,
    period: str
) -> bool:
    """
    Valida que NO existe tarifa para este APS y período
    
    Returns: True si no existe (puede crear)
    Raises: TariffAlreadyExistsError si ya existe
    """
    
    statement = select(TariffCalculation).where(
        (TariffCalculation.aps_id == aps_id) &
        (TariffCalculation.period == period)
    )
    
    existing_tariff = session.exec(statement).first()
    
    if existing_tariff:
        raise TariffAlreadyExistsError(aps_id, period)
    
    return True


def validate_tariff_calculation_input(input_data: dict) -> dict:
    """
    Valida datos de entrada para cálculo
    Asegura valores dentro de rangos razonables
    
    Returns: input_data si es válido
    Raises: ValidationError si hay problemas
    """
    
    from .exceptions import InvalidInputDataError
    
    errors = {}
    
    # Validar distancia
    if input_data.get('distance_km', 0) < 0.5:
        errors['distance_km'] = "Distancia mínima: 0.5 km"
    
    if input_data.get('distance_km', 0) > 500:
        errors['distance_km'] = "Distancia máxima: 500 km"
    
    # Validar toneladas
    if input_data.get('avg_tons_collected', 0) <= 0:
        errors['avg_tons_collected'] = "Toneladas debe ser > 0"
    
    if input_data.get('avg_tons_landfill', 0) <= 0:
        errors['avg_tons_landfill'] = "Toneladas en relleno debe ser > 0"
    
    # Validar escenario CTL
    ctl_scenario = input_data.get('ctl_scenario', 1)
    if not (1 <= ctl_scenario <= 5):
        errors['ctl_scenario'] = "Escenario debe estar entre 1 y 5"
    
    # Validar función CRT
    crt_function = input_data.get('crt_function', 'f1')
    if crt_function not in ['f1', 'f2']:
        errors['crt_function'] = "Función debe ser 'f1' o 'f2'"
    
    # Validar rangos de factor
    subsidy_factor = input_data.get('subsidy_contribution_factor', 0)
    if not (-1 <= subsidy_factor <= 1):
        errors['subsidy_contribution_factor'] = "Factor debe estar entre -1 y 1"
    
    # Validar inflación
    inflation = input_data.get('inflation_rate', 0)
    if not (0 <= inflation <= 1):
        errors['inflation_rate'] = "Tasa de inflación debe estar entre 0 y 1"
    
    if errors:
        raise InvalidInputDataError(errors)
    
    return input_data
