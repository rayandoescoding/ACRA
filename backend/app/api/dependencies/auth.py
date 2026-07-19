"""FastAPI dependencies for authenticated users and role checks."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import InvalidAccessTokenError, decode_access_token
from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve a valid bearer token to an active application user."""
    if credentials is None:
        raise _unauthorized()

    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidAccessTokenError as exc:
        raise _unauthorized() from exc

    user = await AuthService(db).get_active_user(user_id)
    if user is None:
        raise _unauthorized()
    return user


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    """Build a dependency that permits only the supplied application roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
