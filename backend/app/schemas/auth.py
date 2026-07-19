"""Request and response contracts for authentication."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole


class LoginRequest(BaseModel):
    """Credentials accepted by the login endpoint."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=1_024)


class AccessTokenResponse(BaseModel):
    """Bearer token returned after successful credential validation."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(ge=1)


class AuthenticatedUserResponse(BaseModel):
    """Safe representation of an authenticated internal user."""

    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
