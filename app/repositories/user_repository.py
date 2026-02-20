from typing import Optional, List
from sqlmodel import Session, select
from ..models.user import User, Role


class UserRepository:
    """Data access layer for User model - single-tenant per company"""
    
    def __init__(self, session: Session):
        """Initialize repository with session."""
        self.session = session

    def get_all(self, role_filter: Optional[Role] = None) -> List[User]:
        """Get all users (filtered by role if provided)"""
        statement = select(User)
        if role_filter:
            statement = statement.where(User.role == role_filter)
        return self.session.exec(statement.order_by(User.username)).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.exec(
            select(User).where(User.id == user_id)
        ).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.exec(
            select(User).where(User.username == username)
        ).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.exec(
            select(User).where(User.email == email)
        ).first()

    def get_by_role(self, role: Role) -> List[User]:
        """Get all users with specific role"""
        return self.session.exec(
            select(User).where(User.role == role).order_by(User.username)
        ).all()

    def filter_by_company(self, company_id: int) -> List[User]:
        """Filter users by company"""
        return self.session.exec(
            select(User).where(User.company_id == company_id).order_by(User.username)
        ).all()

    def get_system_users(self) -> List[User]:
        """Get all SYSTEM users (company_id is NULL)"""
        return self.session.exec(
            select(User).where(User.company_id == None).where(User.role == Role.SYSTEM)
        ).all()

    def create(self, user: User) -> User:
        """Create a new user"""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Update an existing user"""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete a user"""
        self.session.delete(user)
        self.session.commit()

