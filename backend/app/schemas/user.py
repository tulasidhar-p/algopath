from datetime import datetime, date
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, EmailStr

# Generic API Response wrapper for consistent styling
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool
    streak_count: int
    last_active: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuthData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuthResponse(APIResponse[AuthData]):
    pass
