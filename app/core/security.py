from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_in_production_please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    company_id: Optional[int] = None,
    role: str = "user",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT access token without tenant_id.
    
    Args:
        subject: User ID (as string)
        company_id: Company ID (NULL for SYSTEM users)
        role: User role (system, admin, user)
        expires_delta: Custom expiration time
    """
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "company_id": company_id,  # NULL for SYSTEM
        "role": role,  # For fast validation
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        from jose.exceptions import JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.JWTError:
        raise Exception("Invalid token")
