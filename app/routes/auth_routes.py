from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from ..controllers.auth_controller import authenticate_user, create_token_for_user
from ..core.deps import get_current_user, get_session
from ..models.user import Role
from ..schemas.user import UserRead
from ..repositories.user_repository import UserRepository
from ..core.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
)

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=TokenResponse)
def login(form_data: LoginRequest, session: Session = Depends(get_session)):
    """
    Authenticate user and return JWT token.
    
    In single-tenant mode, the database contains users from a single company.
    """
    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
        session=session
    )
    
    if not user:
        raise InvalidCredentialsError()
    
    if not user.is_active:
        raise UserInactiveError()
    
    token = create_token_for_user(user)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user)
    }


@router.get("/me", response_model=UserRead)
def get_current_user_info(user = Depends(get_current_user)) -> UserRead:
    """Get information about the current authenticated user"""
    return UserRead.model_validate(user)
