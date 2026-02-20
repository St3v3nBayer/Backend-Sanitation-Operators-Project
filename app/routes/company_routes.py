from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from typing import List

from ..core.deps import get_current_user, get_session, require_system_user
from ..models.user import User, Role
from ..schemas.company import CompanyCreate, CompanyUpdate, CompanyRead
from ..core.exceptions import (
    InsufficientPermissionsError,
    CompanyNotFoundError,
    CompanyUpdateError,
    DatabaseError,
)
from ..controllers.company_controller import (
    list_companies,
    get_company,
    create_company,
    update_company,
    delete_company,
)
from ..repositories.audit_log_repository import AuditLogRepository

router = APIRouter()


@router.get("/", response_model=List[CompanyRead])
def list_companies_route(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List companies - SYSTEM sees all, ADMIN sees own, USER forbidden"""
    if user.role == Role.USER:
        raise InsufficientPermissionsError("Usuarios no pueden listar empresas")
    
    try:
        companies = list_companies(session=session)
        if user.role == Role.ADMIN:
            companies = [c for c in companies if c.id == user.company_id]
        return [CompanyRead.model_validate(c) for c in companies]
    except Exception as e:
        raise DatabaseError(str(e))


@router.get("/{company_id}", response_model=CompanyRead)
def get_company_route(
    company_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get specific company"""
    try:
        company = get_company(company_id, session=session)
        if not company:
            raise CompanyNotFoundError(company_id)
        
        if user.role == Role.ADMIN and company.id != user.company_id:
            raise CompanyNotFoundError(company_id)
        
        if user.role == Role.USER:
            raise InsufficientPermissionsError("Usuarios no pueden ver detalles de empresas")
        
        return CompanyRead.model_validate(company)
    except Exception as e:
        raise DatabaseError(str(e))


@router.post("/", status_code=201, response_model=CompanyRead)
def create_company_route(
    payload: CompanyCreate,
    request: Request,
    user: User = Depends(require_system_user),
    session: Session = Depends(get_session),
):
    """Create company (SYSTEM only)"""
    try:
        created = create_company(payload, session=session)
        
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=created.id,
            action="CREATE",
            resource_type="Company",
            resource_id=created.id,
            new_values={"name": created.name, "nit": created.nit},
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
        
        return CompanyRead.model_validate(created)
    except ValueError as e:
        raise CompanyUpdateError(str(e))


@router.put("/{company_id}", response_model=CompanyRead)
def update_company_route(
    company_id: int,
    payload: CompanyUpdate,
    request: Request,
    user: User = Depends(require_system_user),
    session: Session = Depends(get_session),
):
    """Update company (SYSTEM only)"""
    try:
        company = get_company(company_id, session=session)
        if not company:
            raise CompanyNotFoundError(company_id)
        
        updated = update_company(company_id, payload, session=session)
        
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=company_id,
            action="UPDATE",
            resource_type="Company",
            resource_id=company_id,
            old_values={"name": company.name},
            new_values={"name": updated.name if updated else None},
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
        
        return CompanyRead.model_validate(updated)
    except ValueError as e:
        raise CompanyUpdateError(str(e))


@router.delete("/{company_id}", status_code=204)
def delete_company_route(
    company_id: int,
    request: Request,
    user: User = Depends(require_system_user),
    session: Session = Depends(get_session),
):
    """Delete company (SYSTEM only)"""
    try:
        company = get_company(company_id, session=session)
        if not company:
            raise CompanyNotFoundError(company_id)
        
        delete_company(company_id, session=session)
        
        audit_repo = AuditLogRepository(session)
        audit_repo.log_action(
            user_id=user.id,
            company_id=company_id,
            action="DELETE",
            resource_type="Company",
            resource_id=company_id,
            old_values={"name": company.name, "nit": company.nit},
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
    except ValueError as e:
        raise CompanyUpdateError(str(e))
