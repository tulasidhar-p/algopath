from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.services.auth_service import AuthService, UserAlreadyExistsError, InvalidCredentialsError
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Validate user registration credentials, normalize the email, hash the password, initialize topic progress records, and create a user profile in the database.",
    responses={
        409: {"description": "Conflict - User with this email already exists"},
        422: {"description": "Unprocessable Entity - Schema validation failed"}
    }
)
def register(register_data: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Register a new user account."""
    try:
        return AuthService.register_user(db, register_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from e

@router.post(
    "/login", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK,
    summary="Log in a user",
    description="Authenticate user credentials against hashed password records and issue a cryptographically signed JWT access token.",
    responses={
        401: {"description": "Unauthorized - Invalid email or password"},
        422: {"description": "Unprocessable Entity - Schema validation failed"}
    }
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate and log in a user."""
    try:
        return AuthService.login_user(db, login_data)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from e

@router.get(
    "/me", 
    response_model=UserResponse, 
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user session",
    description="Verify active JSON Web Token authorization header and retrieve user details for the active session.",
    responses={
        401: {"description": "Unauthorized - Missing, expired, or invalid credentials"}
    }
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Retrieve details of the currently logged-in user."""
    # Convert ORM user to Pydantic UserResponse DTO
    return UserResponse.model_validate(current_user)
