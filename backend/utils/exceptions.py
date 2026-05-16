
from fastapi import HTTPException, status
from typing import Optional

class BaseAppException(HTTPException):
    """Base class for all custom application exceptions."""
    def __init__(self, status_code: int, detail: str, headers: Optional[dict] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InvalidCredentialsError(BaseAppException):
    """Raised when login credentials (username/email or password) are incorrect."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

class TokenExpiredError(BaseAppException):
    """Raised when a JWT token has passed its expiration time."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again."
        )

class InvalidTokenError(BaseAppException):
    """Raised when a JWT token is malformed, tampered with, or invalid."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed authentication token."
        )


class UserNotFoundError(BaseAppException):
    """Raised when a requested user does not exist in the database."""
    def __init__(self, identifier: str = "user"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{identifier.capitalize()} not found."
        )

class UserAlreadyExistsError(BaseAppException):
    """Raised when attempting to register with an existing username or email."""
    def __init__(self, field: str = "username or email"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with this {field} already exists."
        )

class UserInactiveError(BaseAppException):
    """Raised when attempting to log in or perform actions with a deactivated/banned account."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated or banned. Contact support."
        )


class PermissionDeniedError(BaseAppException):
    """Raised when a user tries to access a resource without sufficient privileges."""
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class AdminOnlyError(BaseAppException):
    """Raised when an endpoint requires administrator privileges."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required."
        )


class ResourceNotFoundError(BaseAppException):
    """Generic exception for missing resources (messages, groups, files, etc.)."""
    def __init__(self, resource_name: str = "resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name.capitalize()} not found."
        )

class ResourceConflictError(BaseAppException):
    """Raised when an operation conflicts with the current state of a resource."""
    def __init__(self, detail: str = "Operation conflicts with existing data."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

class RateLimitExceededError(BaseAppException):
    """Raised when too many requests are made in a short timeframe."""
    def __init__(self, retry_after: Optional[int] = None):
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
            headers=headers
        )