"""Authentication request and response validation schemas.

This module defines Pydantic validation models for registration requests,
login requests, token responses, and user profiles.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Validation schema for user registration requests."""

    name: str = Field(..., description="The user's display name.")
    email: EmailStr = Field(..., description="The user's unique email address.")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The user's password, between 8 and 128 characters.",
    )


class LoginRequest(BaseModel):
    """Validation schema for user authentication requests."""

    email: EmailStr = Field(..., description="The user's registered email address.")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The user's password.",
    )


class UserResponse(BaseModel):
    """Pydantic model representing a sanitized user entity in responses."""

    id: int
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    is_admin: Optional[bool] = False
    streak_count: Optional[int] = 0
    last_active: Optional[date] = None

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class TokenResponse(BaseModel):
    """Response model returning the JWT token metadata."""

    access_token: str
    token_type: str = Field("bearer", description="The type of token returned.")
