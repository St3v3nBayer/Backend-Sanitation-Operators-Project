"""
Error handler middleware y utils para respuestas estandarizadas
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
from datetime import datetime

from .exceptions import SanitationSystemError

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Formato estandarizado de respuestas de error"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        details: dict = None,
        timestamp: str = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow().isoformat()
    
    def to_dict(self):
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        }


def register_exception_handlers(app: FastAPI):
    """
    Registra handlers de excepciones centralizados
    """
    
    # Handler para excepciones del sistema
    @app.exception_handler(SanitationSystemError)
    async def sanitation_exception_handler(request: Request, exc: SanitationSystemError):
        logger.warning(
            f"[{exc.error_code}] {exc.message}",
            extra={"details": exc.details}
        )
        
        error_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(error_response.to_dict())
        )
    
    # Handler para excepciones no capturadas
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True
        )
        
        error_response = ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="Se produjo un error interno. Por favor intenta más tarde.",
            status_code=500,
            details={"error_type": exc.__class__.__name__}
        )
        
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error_response.to_dict())
        )
