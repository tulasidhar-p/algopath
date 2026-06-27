from app.schemas.user import UserRegister, UserLogin, UserResponse as LegacyUserResponse, AuthData, AuthResponse, APIResponse
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse

__all__ = [
    "UserRegister",
    "UserLogin",
    "LegacyUserResponse",
    "AuthData",
    "AuthResponse",
    "APIResponse",
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "TokenResponse",
]

