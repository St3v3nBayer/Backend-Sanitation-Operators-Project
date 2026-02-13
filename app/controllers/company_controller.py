from typing import List, Optional
from sqlmodel import Session
from ..models.company import Company
from ..repositories.company_repository import CompanyRepository


def list_companies(session: Optional[Session] = None) -> List[Company]:
    repo = CompanyRepository(session=session)
    return repo.get_all()


def get_company(company_id: int, session: Optional[Session] = None) -> Optional[Company]:
    repo = CompanyRepository(session=session)
    return repo.get_by_id(company_id)


def create_company(payload: dict, session: Optional[Session] = None) -> Company:
    company = Company(**payload)
    repo = CompanyRepository(session=session)
    return repo.create(company)


def update_company(company_id: int, payload: dict, session: Optional[Session] = None) -> Optional[Company]:
    repo = CompanyRepository(session=session)
    return repo.update(company_id, payload)


def delete_company(company_id: int, session: Optional[Session] = None) -> bool:
    repo = CompanyRepository(session=session)
    return repo.delete(company_id)
