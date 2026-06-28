import pytest
from jose import jwt
from app.services.jwt_service import JWTService, TokenExpiredError, TokenInvalidError
from app.config.settings import settings

def test_create_access_token_success():
    subject = "user@example.com"
    token = JWTService.create_access_token(subject)
    assert len(token) > 0
    
    # Decode directly using python-jose to verify fields
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == subject
    assert "exp" in decoded
    # JWT payload should contain ONLY 'sub' and 'exp'
    assert set(decoded.keys()) == {"sub", "exp"}

def test_verify_access_token_valid():
    subject = "test-user-id"
    token = JWTService.create_access_token(subject)
    payload = JWTService.verify_access_token(token)
    assert payload["sub"] == subject

def test_verify_access_token_expired(monkeypatch):
    subject = "expired-user"
    # Set expiration in the past to create an expired token
    monkeypatch.setattr(JWTService, "ACCESS_TOKEN_EXPIRE_MINUTES", -5)
    expired_token = JWTService.create_access_token(subject)
    
    with pytest.raises(TokenExpiredError) as exc_info:
        JWTService.verify_access_token(expired_token)
    assert "expired" in str(exc_info.value).lower()

def test_verify_access_token_invalid_signature():
    subject = "user"
    token = JWTService.create_access_token(subject)
    
    # Tamper with the token to invalidate signature
    invalid_token = token + "tampered"
    with pytest.raises(TokenInvalidError) as exc_info:
        JWTService.verify_access_token(invalid_token)
    assert "invalid" in str(exc_info.value).lower()

def test_verify_access_token_malformed():
    with pytest.raises(TokenInvalidError):
        JWTService.verify_access_token("not-a-valid-jwt-token")

def test_decode_access_token_expired(monkeypatch):
    subject = "expired-decode-user"
    monkeypatch.setattr(JWTService, "ACCESS_TOKEN_EXPIRE_MINUTES", -10)
    expired_token = JWTService.create_access_token(subject)
    
    # verify_access_token raises TokenExpiredError
    with pytest.raises(TokenExpiredError):
        JWTService.verify_access_token(expired_token)
        
    # decode_access_token successfully decodes expired token
    payload = JWTService.decode_access_token(expired_token)
    assert payload["sub"] == subject
