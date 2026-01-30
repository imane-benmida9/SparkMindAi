from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: Any, extra_claims: dict[str, Any] | None = None) -> str:
    """
    Create a JWT access token.
    Ensure non-JSON types (UUID, datetime) are converted to serializable types.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Convert subject (UUID or other) to string to ensure JSON serializable
    sub = str(subject)
    # Use UNIX timestamp for exp to guarantee JSON serializability
    to_encode: dict[str, Any] = {"sub": sub, "exp": int(expire.timestamp())}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: Any) -> str:
    """Create a JWT refresh token; convert subject and exp to serializable types."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    sub = str(subject)
    to_encode: dict[str, Any] = {"sub": sub, "exp": int(expire.timestamp()), "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e
