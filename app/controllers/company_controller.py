from typing import List, Optional
from sqlmodel import Session
from ..models.company import Company
from ..repositories.company_repository import CompanyRepository
from ..schemas.company import CompanyCreate, CompanyUpdate


def list_companies(session: Session) -> List[Company]:
    repo = CompanyRepository(session=session)
    return repo.get_all()


def get_company(company_id: int, session: Session) -> Optional[Company]:
    repo = CompanyRepository(session=session)
    return repo.get_by_id(company_id)


def create_company(data: CompanyCreate, session: Session) -> Company:
    """Create new company with NIT/name uniqueness validation"""
    repo = CompanyRepository(session=session)
    
    # Check if NIT already exists
    existing = repo.get_by_nit(data.nit)
    if existing:
        raise ValueError(f"Company with NIT {data.nit} already exists")
    
    # Check if name already exists
    existing = repo.get_by_name(data.name)
    if existing:
        raise ValueError(f"Company with name {data.name} already exists")
    
    company = Company(
        name=data.name,
        nit=data.nit,
        is_active=True
    )
    return repo.create(company)


def update_company(company_id: int, data: CompanyUpdate, session: Session) -> Optional[Company]:
    """Update company with validation"""
    repo = CompanyRepository(session=session)
    company = repo.get_by_id(company_id)
    
    if not company:
        return None
    
    # Validate NIT uniqueness if changing
    if data.nit and data.nit != company.nit:
        existing = repo.get_by_nit(data.nit)
        if existing:
            raise ValueError(f"Company with NIT {data.nit} already exists")
    
    # Validate name uniqueness if changing
    if data.name and data.name != company.name:
        existing = repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Company with name {data.name} already exists")
    
    # Build update dict (only non-None values)
    update_data = {}
    if data.name:
        update_data["name"] = data.name
    if data.nit:
        update_data["nit"] = data.nit
    if data.is_active is not None:
        update_data["is_active"] = data.is_active
    
    return repo.update(company_id, update_data)


def delete_company(company_id: int, session: Session) -> bool:
    repo = CompanyRepository(session=session)
    return repo.delete(company_id)
