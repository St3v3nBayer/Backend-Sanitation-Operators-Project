from typing import List, Optional
from sqlmodel import Session, select
from ..models.company import Company
from ..db import engine


class CompanyRepository:
    def __init__(self, session: Optional[Session] = None):
        """
        Inicializa repository con sesión.
        
        Si session es None, usa el engine por defecto (desarrollo).
        Si session se proporciona, la usa (producción multi-tenant).
        """
        self._session = session
        self._owns_session = session is None
        if session is None:
            self._session = Session(engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session:
            self._session.close()

    def get_all(self) -> List[Company]:
        statement = select(Company)
        result = self._session.exec(statement).all()
        return result

    def get_by_id(self, company_id: int) -> Optional[Company]:
        return self._session.get(Company, company_id)

    def create(self, company: Company) -> Company:
        self._session.add(company)
        self._session.commit()
        self._session.refresh(company)
        return company

    def update(self, company_id: int, data: dict) -> Optional[Company]:
        company = self._session.get(Company, company_id)
        if not company:
            return None
        for key, value in data.items():
            setattr(company, key, value)
        self._session.add(company)
        self._session.commit()
        self._session.refresh(company)
        return company

    def delete(self, company_id: int) -> bool:
        company = self._session.get(Company, company_id)
        if not company:
            return False
        self._session.delete(company)
        self._session.commit()
        return True
