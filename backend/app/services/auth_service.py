from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.models.user import User

class AuthenticationError(Exception):
    """Base exception for authentication business logic errors."""
    pass

class UserAlreadyExistsError(AuthenticationError):
    """Raised when registering with an email that is already in use."""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Raised for authentication failures due to invalid credentials (username or password)."""
    pass

class UserNotFoundError(AuthenticationError):
    """Raised when a user cannot be found in the database."""
    pass

class AuthService:
    """Orchestration layer for user authentication and account management.

    This service is stateless and independent of FastAPI framework classes/exceptions.
    """

    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize an email address by stripping whitespace and converting to lowercase.

        Args:
            email: The raw email string.

        Returns:
            The normalized email string.
        """
        return email.strip().lower()

    @classmethod
    def register_user(cls, db: Session, register_data: RegisterRequest) -> UserResponse:
        """Register a new user in the system.

        Args:
            db: SQLAlchemy database session.
            register_data: Registration request containing name, email, and password.

        Returns:
            UserResponse: The DTO representing the newly created user.

        Raises:
            UserAlreadyExistsError: If the normalized email is already registered.
            AuthenticationError: If registration fails due to database errors.
        """
        normalized_email = cls._normalize_email(register_data.email)
        
        # Check if email already exists
        existing_user = user_repo.get_user_by_email(db, normalized_email)
        if existing_user:
            raise UserAlreadyExistsError("A user with this email address already exists")

        # Hash password using PasswordService
        hashed_password = PasswordService.hash_password(register_data.password)

        try:
            # Create user (which calls db.commit() internally in the repo)
            user = user_repo.create_user(
                db, 
                name=register_data.name, 
                email=normalized_email, 
                hashed_password=hashed_password
            )
            
            # Initialize progress. If it fails, delete the created user to maintain consistency.
            try:
                user_repo.initialize_user_topic_progress(db, user.id)
            except Exception as progress_exc:
                db.delete(user)
                db.commit()
                raise progress_exc
                
            return UserResponse.model_validate(user)
        except Exception as e:
            db.rollback()
            raise AuthenticationError("Failed to register user due to a database error") from e

    @classmethod
    def login_user(cls, db: Session, login_data: LoginRequest) -> TokenResponse:
        """Authenticate a user and return a JWT access token.

        Args:
            db: SQLAlchemy database session.
            login_data: Login credentials (email and password).

        Returns:
            TokenResponse: The token metadata DTO.

        Raises:
            InvalidCredentialsError: If the email is unknown or password is incorrect.
        """
        normalized_email = cls._normalize_email(login_data.email)
        
        # Retrieve user by email
        user = user_repo.get_user_by_email(db, normalized_email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        # Verify password using PasswordService
        if not PasswordService.verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        # Generate JWT using JWTService
        access_token = JWTService.create_access_token(user.email)
        return TokenResponse(access_token=access_token, token_type="bearer")

    @classmethod
    def get_user_by_email(cls, db: Session, email: str) -> User:
        """Retrieve the ORM User model by their email address.

        Args:
            db: SQLAlchemy database session.
            email: The email address to look up.

        Returns:
            User: The ORM User model instance.

        Raises:
            UserNotFoundError: If the user is not found.
        """
        normalized_email = cls._normalize_email(email)
        user = user_repo.get_user_by_email(db, normalized_email)
        if not user:
            raise UserNotFoundError(f"User with email '{normalized_email}' not found")
        return user

    @classmethod
    def get_user_by_id(cls, db: Session, user_id: int) -> User:
        """Retrieve the ORM User model by their unique identifier.

        Args:
            db: SQLAlchemy database session.
            user_id: The ID of the user.

        Returns:
            User: The ORM User model instance.

        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user
