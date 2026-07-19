"""Authentication endpoints for internal ACRA users."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.core.security import create_access_token
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    AuthenticatedUserResponse,
    LoginRequest,
)
from app.services.auth_service import AuthService, InvalidCredentialsError


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate an internal user",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AccessTokenResponse:
    """Validate credentials and return a short-lived bearer token."""
    try:
        user = await AuthService(db).authenticate(
            credentials.email,
            credentials.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token, expires_in = create_access_token(user.id, user.role)
    return AccessTokenResponse(access_token=access_token, expires_in=expires_in)


@router.get(
    "/me",
    response_model=AuthenticatedUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's safe identity representation."""
    return current_user
