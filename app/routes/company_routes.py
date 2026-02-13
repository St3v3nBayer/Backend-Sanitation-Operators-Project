from fastapi import APIRouter, HTTPException, Depends
from ..core.deps import get_current_user_with_tenant
from typing import List
from ..schemas.company import CompanyCreate, CompanyUpdate, CompanyRead
from ..controllers.company_controller import (
    list_companies,
    get_company,
    create_company,
    update_company,
    delete_company,
)

# Protect all company routes: require authenticated user from correct tenant
router = APIRouter()


@router.get("/", response_model=List[CompanyRead])
def companies_list(user_data = Depends(get_current_user_with_tenant)):
    current_user, tenant_session, tenant_id = user_data
    companies = list_companies(session=tenant_session)
    return [CompanyRead.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyRead)
def companies_get(company_id: int, user_data = Depends(get_current_user_with_tenant)):
    current_user, tenant_session, tenant_id = user_data
    company = get_company(company_id, session=tenant_session)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyRead.model_validate(company)


@router.post("/", status_code=201, response_model=CompanyRead)
def companies_create(payload: CompanyCreate, user_data = Depends(get_current_user_with_tenant)):
    current_user, tenant_session, tenant_id = user_data
    created = create_company(payload.model_dump(), session=tenant_session)
    return CompanyRead.model_validate(created)


@router.put("/{company_id}", response_model=CompanyRead)
def companies_update(company_id: int, payload: CompanyUpdate, user_data = Depends(get_current_user_with_tenant)):
    current_user, tenant_session, tenant_id = user_data
    updated = update_company(company_id, payload.model_dump(exclude_unset=True), session=tenant_session)
    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyRead.model_validate(updated)


@router.delete("/{company_id}", status_code=204)
def companies_delete(company_id: int, user_data = Depends(get_current_user_with_tenant)):
    current_user, tenant_session, tenant_id = user_data
    ok = delete_company(company_id, session=tenant_session)
    if not ok:
        raise HTTPException(status_code=404, detail="Company not found")
    return None
