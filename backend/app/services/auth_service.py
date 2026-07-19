"""Authentication persistence and credential-verification operations."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole


class InvalidCredentialsError(ValueError):
    """Raised when login credentials cannot authenticate a user."""


class AuthService:
    """Encapsulates user authentication without exposing password hashes."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def authenticate(self, email: str, password: str) -> User:
        """Return an active user with matching credentials or raise a safe error."""
        user = await self._get_user_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password.")
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password.")
        return user

    async def get_active_user(self, user_id: UUID) -> User | None:
        """Load an active user by JWT subject identifier."""
        user = await self._db.get(User, user_id)
        if user is None or not user.is_active:
            return None
        return user

    async def ensure_bootstrap_admin(
        self,
        *,
        email: str | None,
        password: str | None,
    ) -> bool:
        """Create the initial administrator only when no users exist."""
        if not email or not password:
            return False

        user_count = await self._db.scalar(select(func.count(User.id)))
        if user_count:
            return False

        normalized_email = self._normalize_email(email)
        if not normalized_email:
            return False

        admin = User(
            email=normalized_email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        self._db.add(admin)
        try:
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            return False
        return True

    async def _get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == self._normalize_email(email))
        return await self._db.scalar(statement)

    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize case and surrounding whitespace before identity lookup."""
        return email.strip().casefold()
