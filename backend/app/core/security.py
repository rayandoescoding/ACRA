"""Password hashing and JWT utilities for application authentication."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.models.user import UserRole


class InvalidAccessTokenError(ValueError):
    """Raised when an access token cannot be trusted."""


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return an Argon2 hash for a plaintext password."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: UUID, role: UserRole) -> tuple[str, int]:
    """Create a signed, expiring JWT access token for an active user."""
    now = datetime.now(timezone.utc)
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expires_at = now + timedelta(seconds=expires_in)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": role.value,
            "type": "access",
            "iat": now,
            "exp": expires_at,
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, expires_in


def decode_access_token(token: str) -> UUID:
    """Validate an access token and return its authenticated subject UUID."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise InvalidAccessTokenError("Token is not an access token.")
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise InvalidAccessTokenError("Access token is invalid or expired.") from exc
