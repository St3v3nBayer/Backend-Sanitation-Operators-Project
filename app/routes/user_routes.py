from fastapi import APIRouter, HTTPException, Depends
from ..schemas.user import UserCreate, UserUpdate, UserRead
from ..controllers.user_controller import (
    list_users,
    get_user,
    create_user,
    update_user,
    delete_user,
)
from ..core.deps import get_current_user_with_tenant

router = APIRouter()


@router.get("", response_model=list[UserRead])
def list_users_endpoint(user_data = Depends(get_current_user_with_tenant)):
    """List all users for the current tenant"""
    user, session, tenant_id = user_data
    try:
        users = list_users(tenant_id, session=session)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserRead)
def get_user_endpoint(user_id: int, user_data = Depends(get_current_user_with_tenant)):
    """Get a specific user"""
    user, session, tenant_id = user_data
    try:
        user_obj = get_user(user_id, tenant_id, session=session)
        return user_obj
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=UserRead, status_code=201)
def create_user_endpoint(
    data: UserCreate,
    user_data = Depends(get_current_user_with_tenant)
):
    """Create a new user in the current tenant"""
    user, session, tenant_id = user_data
    try:
        new_user = create_user(data, tenant_id, session=session)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: int,
    data: UserUpdate,
    user_data = Depends(get_current_user_with_tenant)
):
    """Update an existing user"""
    user, session, tenant_id = user_data
    try:
        updated_user = update_user(user_id, tenant_id, data, session=session)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user_endpoint(
    user_id: int,
    user_data = Depends(get_current_user_with_tenant)
):
    """Delete a user"""
    user, session, tenant_id = user_data
    try:
        delete_user(user_id, tenant_id, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
