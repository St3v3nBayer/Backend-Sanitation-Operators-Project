"""
Custom exceptions para el sistema de tarifas
Centralizadas para manejo consistente de errores
"""


class SanitationSystemError(Exception):
    """Excepción base del sistema"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SYSTEM_ERROR",
        status_code: int = 500,
        details: dict = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ========================================
# APS RELATED ERRORS
# ========================================

class APSNotFoundError(SanitationSystemError):
    """APS no existe"""
    
    def __init__(self, aps_id: int):
        super().__init__(
            message=f"APS con ID {aps_id} no encontrado",
            error_code="APS_NOT_FOUND",
            status_code=404,
            details={"aps_id": aps_id}
        )


class APSAccessDeniedError(SanitationSystemError):
    """Usuario no tiene acceso al APS"""
    
    def __init__(self, aps_id: int, user_id: int):
        super().__init__(
            message=f"No tienes permiso para acceder al APS {aps_id}",
            error_code="APS_ACCESS_DENIED",
            status_code=403,
            details={"aps_id": aps_id, "user_id": user_id}
        )


class APSNotBelongsToCompanyError(SanitationSystemError):
    """APS no pertenece a la empresa del usuario"""
    
    def __init__(self, aps_id: int, company_id: int):
        super().__init__(
            message=f"APS {aps_id} no pertenece a tu empresa",
            error_code="APS_COMPANY_MISMATCH",
            status_code=403,
            details={"aps_id": aps_id, "company_id": company_id}
        )


# ========================================
# TARIFF CALCULATION ERRORS
# ========================================

class InvalidPeriodError(SanitationSystemError):
    """Período inválido (debe ser YYYY-MM)"""
    
    def __init__(self, period: str):
        super().__init__(
            message=f"Período '{period}' inválido. Usa formato YYYY-MM (ej: 2026-01)",
            error_code="INVALID_PERIOD_FORMAT",
            status_code=400,
            details={"period": period}
        )


class TariffAlreadyExistsError(SanitationSystemError):
    """Ya existe una tarifa para este período y APS"""
    
    def __init__(self, aps_id: int, period: str):
        super().__init__(
            message=f"Ya existe una tarifa para APS {aps_id} en período {period}",
            error_code="TARIFF_ALREADY_EXISTS",
            status_code=409,
            details={"aps_id": aps_id, "period": period}
        )


class TariffCalculationError(SanitationSystemError):
    """Error durante el cálculo de la tarifa"""
    
    def __init__(self, reason: str, details: dict = None):
        super().__init__(
            message=f"Error al calcular tarifa: {reason}",
            error_code="TARIFF_CALCULATION_ERROR",
            status_code=422,
            details=details or {}
        )


class TariffNotFoundError(SanitationSystemError):
    """Tarifa no encontrada"""
    
    def __init__(self, tariff_id: int):
        super().__init__(
            message=f"Tarifa con ID {tariff_id} no encontrada",
            error_code="TARIFF_NOT_FOUND",
            status_code=404,
            details={"tariff_id": tariff_id}
        )


# ========================================
# VALIDATION ERRORS
# ========================================

class ValidationError(SanitationSystemError):
    """Error de validación de datos"""
    
    def __init__(self, field: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Validación fallida en '{field}': {reason}",
            error_code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field, "reason": reason, **(details or {})}
        )


class InvalidInputDataError(SanitationSystemError):
    """Datos de entrada inválidos para cálculo"""
    
    def __init__(self, errors: dict):
        super().__init__(
            message="Los parámetros de cálculo contienen errores",
            error_code="INVALID_INPUT_DATA",
            status_code=422,
            details={"validation_errors": errors}
        )


# ========================================
# AUTHENTICATION & AUTHORIZATION
# ========================================

class UnauthorizedError(SanitationSystemError):
    """Usuario no autenticado"""
    
    def __init__(self):
        super().__init__(
            message="Usuario no autenticado",
            error_code="UNAUTHORIZED",
            status_code=401
        )


class ForbiddenError(SanitationSystemError):
    """Usuario no tiene permiso"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Acceso denegado: {reason}",
            error_code="FORBIDDEN",
            status_code=403
        )


# ========================================
# DATABASE ERRORS
# ========================================

class DatabaseError(SanitationSystemError):
    """Error de base de datos"""
    
    def __init__(self, reason: str, details: dict = None):
        super().__init__(
            message=f"Error de base de datos: {reason}",
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details or {}
        )


class RecordNotFoundError(SanitationSystemError):
    """Registro no encontrado en BD"""
    
    def __init__(self, entity: str, entity_id: int):
        super().__init__(
            message=f"{entity} con ID {entity_id} no encontrado",
            error_code="RECORD_NOT_FOUND",
            status_code=404,
            details={"entity": entity, "entity_id": entity_id}
        )


# ========================================
# TENANT ERRORS
# ========================================

class TenantNotFoundError(SanitationSystemError):
    """Tenant no encontrado"""
    
    def __init__(self, tenant_id: int):
        super().__init__(
            message=f"Tenant con ID {tenant_id} no encontrado",
            error_code="TENANT_NOT_FOUND",
            status_code=404,
            details={"tenant_id": tenant_id}
        )


class TenantCreationError(SanitationSystemError):
    """Error en creación de tenant"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Error al crear tenant: {reason}",
            error_code="TENANT_CREATION_ERROR",
            status_code=400,
            details={"reason": reason}
        )


# ========================================
# COMPANY ERRORS
# ========================================

class CompanyNotFoundError(SanitationSystemError):
    """Empresa no encontrada"""
    
    def __init__(self, company_id: int):
        super().__init__(
            message=f"Empresa con ID {company_id} no encontrada",
            error_code="COMPANY_NOT_FOUND",
            status_code=404,
            details={"company_id": company_id}
        )


class CompanyAccessDeniedError(SanitationSystemError):
    """Usuario no tiene acceso a la empresa"""
    
    def __init__(self, company_id: int):
        super().__init__(
            message=f"No tienes acceso a la empresa {company_id}",
            error_code="COMPANY_ACCESS_DENIED",
            status_code=403,
            details={"company_id": company_id}
        )


class CompanyUpdateError(SanitationSystemError):
    """Error al actualizar empresa"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Error al actualizar empresa: {reason}",
            error_code="COMPANY_UPDATE_ERROR",
            status_code=400,
            details={"reason": reason}
        )


# ========================================
# USER ERRORS
# ========================================

class UserNotFoundError(SanitationSystemError):
    """Usuario no encontrado"""
    
    def __init__(self, user_id: int):
        super().__init__(
            message=f"Usuario con ID {user_id} no encontrado",
            error_code="USER_NOT_FOUND",
            status_code=404,
            details={"user_id": user_id}
        )


class UserInactiveError(SanitationSystemError):
    """Usuario está inactivo"""
    
    def __init__(self):
        super().__init__(
            message="Usuario está inactivo",
            error_code="USER_INACTIVE",
            status_code=403
        )


class InvalidCredentialsError(SanitationSystemError):
    """Credenciales inválidas"""
    
    def __init__(self):
        super().__init__(
            message="Credenciales inválidas",
            error_code="INVALID_CREDENTIALS",
            status_code=401
        )


class UserCreationError(SanitationSystemError):
    """Error en creación de usuario"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Error al crear usuario: {reason}",
            error_code="USER_CREATION_ERROR",
            status_code=400,
            details={"reason": reason}
        )


class UserAccessDeniedError(SanitationSystemError):
    """Usuario no tiene permiso para acceder a otro usuario"""
    
    def __init__(self, user_id: int):
        super().__init__(
            message=f"No tienes permiso para acceder al usuario {user_id}",
            error_code="USER_ACCESS_DENIED",
            status_code=403,
            details={"user_id": user_id}
        )


class InsufficientPermissionsError(SanitationSystemError):
    """Permisos insuficientes para la operación"""
    
    def __init__(self, reason: str = "Permisos insuficientes"):
        super().__init__(
            message=reason,
            error_code="INSUFFICIENT_PERMISSIONS",
            status_code=403,
            details={"reason": reason}
        )


# ========================================
# AUDIT LOG ERRORS
# ========================================

class AuditLogNotFoundError(SanitationSystemError):
    """Registro de auditoría no encontrado"""
    
    def __init__(self, log_id: int):
        super().__init__(
            message=f"Registro de auditoría con ID {log_id} no encontrado",
            error_code="AUDIT_LOG_NOT_FOUND",
            status_code=404,
            details={"log_id": log_id}
        )


class AuditLogAccessDeniedError(SanitationSystemError):
    """Usuario no tiene acceso al registro de auditoría"""
    
    def __init__(self):
        super().__init__(
            message="No tienes permiso para acceder a registros de auditoría",
            error_code="AUDIT_LOG_ACCESS_DENIED",
            status_code=403
        )


# ========================================
# FEATURE ERRORS
# ========================================

class NotImplementedFeatureError(SanitationSystemError):
    """Funcionalidad no implementada"""
    
    def __init__(self, feature_name: str):
        super().__init__(
            message=f"Funcionalidad no implementada: {feature_name}",
            error_code="NOT_IMPLEMENTED",
            status_code=501,
            details={"feature": feature_name}
        )
