"""Authentication routes endpoints definition.

This module sets up the APIRouter for authentication. In this foundation phase,
no path operations (endpoints) are registered.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
