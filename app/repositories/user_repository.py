from typing import Optional, List
from sqlmodel import Session, select
from ..models.user import User


class UserRepository:
    def __init__(self, session: Session):
        """Initialize repository with session."""
        self.session = session

    def get_all(self, tenant_id: int) -> List[User]:
        """Get all users for a specific tenant."""
        statement = select(User).where(User.tenant_id == tenant_id).order_by(User.username)
        return self.session.exec(statement).all()

    def get_by_id(self, user_id: int, tenant_id: int) -> Optional[User]:
        """Get user by ID, ensuring tenant isolation."""
        statement = select(User).where(
            (User.id == user_id) & (User.tenant_id == tenant_id)
        )
        return self.session.exec(statement).first()

    def get_by_username(self, username: str, tenant_id: int) -> Optional[User]:
        """Get user by username for a tenant."""
        statement = select(User).where(
            (User.username == username) & (User.tenant_id == tenant_id)
        )
        return self.session.exec(statement).first()

    def get_by_email(self, email: str, tenant_id: int) -> Optional[User]:
        """Get user by email for a tenant."""
        statement = select(User).where(
            (User.email == email) & (User.tenant_id == tenant_id)
        )
        return self.session.exec(statement).first()

    def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Update an existing user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete a user."""
        self.session.delete(user)
        self.session.commit()

