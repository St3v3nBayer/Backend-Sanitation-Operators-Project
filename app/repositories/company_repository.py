from typing import List, Optional
from sqlmodel import Session, select
from ..models.company import Company


class CompanyRepository:
    """Data access layer for Company model"""
    
    def __init__(self, session: Session):
        """Initialize repository with session"""
        self.session = session

    def get_all(self) -> List[Company]:
        """Get all companies"""
        return self.session.exec(select(Company).order_by(Company.name)).all()

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.session.get(Company, company_id)

    def get_by_name(self, name: str) -> Optional[Company]:
        """Get company by name"""
        return self.session.exec(
            select(Company).where(Company.name == name)
        ).first()

    def get_by_nit(self, nit: str) -> Optional[Company]:
        """Get company by NIT (Colombian tax ID)"""
        return self.session.exec(
            select(Company).where(Company.nit == nit)
        ).first()

    def get_active(self) -> List[Company]:
        """Get all active companies"""
        return self.session.exec(
            select(Company).where(Company.is_active == True).order_by(Company.name)
        ).all()

    def create(self, company: Company) -> Company:
        """Create a new company"""
        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company

    def update(self, company: Company) -> Company:
        """Update an existing company"""
        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        """Delete a company"""
        self.session.delete(company)
        self.session.commit()

    def delete(self, company_id: int) -> bool:
        company = self._session.get(Company, company_id)
        if not company:
            return False
        self._session.delete(company)
        self._session.commit()
        return True
