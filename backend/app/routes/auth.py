from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, AuthResponse, AuthData, UserResponse, APIResponse
from app.repositories import user_repo
from app.services import auth_service
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = user_repo.get_user_by_email(db, user_in.email)
    if existing_user:
        return {
            "success": False,
            "error": "Email already registered. Please log in."
        }

    # Hash password and create user
    password_hash = auth_service.get_password_hash(user_in.password)
    user = user_repo.create_user(
        db=db,
        name=user_in.name,
        email=user_in.email,
        password_hash=password_hash
    )

    # Initialize user progress records for all topics
    user_repo.initialize_user_topic_progress(db, user.id)

    # Generate JWT token
    access_token = auth_service.create_access_token(data={"sub": user.email})

    user_data = UserResponse.from_orm(user)
    return {
        "success": True,
        "data": AuthData(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
    }

@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # Fetch user
    user = user_repo.get_user_by_email(db, credentials.email)
    if not user or not auth_service.verify_password(credentials.password, user.password_hash):
        return {
            "success": False,
            "error": "Invalid email or password."
        }

    # Make sure progress is initialized (handles legacy users or pre-seeded admins)
    user_repo.initialize_user_topic_progress(db, user.id)

    # Generate JWT token
    access_token = auth_service.create_access_token(data={"sub": user.email})

    user_data = UserResponse.from_orm(user)
    return {
        "success": True,
        "data": AuthData(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
    }

@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(current_user: User = Depends(auth_service.get_current_user)):
    user_data = UserResponse.from_orm(current_user)
    return {
        "success": True,
        "data": user_data
    }
