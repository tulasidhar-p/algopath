from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.jwt_service import JWTService, TokenExpiredError, TokenInvalidError
from app.services.auth_service import AuthService, UserNotFoundError
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI dependency to retrieve the currently authenticated user from a JWT token.

    Args:
        token: The Bearer token extracted from the request headers.
        db: SQLAlchemy database session.

    Returns:
        User: The authenticated User ORM model instance.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
        
    try:
        payload = JWTService.verify_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (TokenExpiredError, TokenInvalidError) as e:
        raise credentials_exception from e

    try:
        # Retrieve user from AuthService
        user = AuthService.get_user_by_email(db, email)
        return user
    except UserNotFoundError as e:
        raise credentials_exception from e

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to verify that the current user has administrator privileges.

    Args:
        current_user: The resolved User model instance from get_current_user.

    Returns:
        User: The authorized User instance.

    Raises:
        HTTPException: 403 Forbidden if the user is not an administrator.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
