from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from app.config.settings import settings

class JWTServiceError(Exception):
    """Base exception class for JWT-related errors."""
    pass

class TokenExpiredError(JWTServiceError):
    """Exception raised when a JWT access token has expired."""
    pass

class TokenInvalidError(JWTServiceError):
    """Exception raised when a JWT access token is malformed, invalid, or has an invalid signature."""
    pass

class JWTService:
    """Stateless utility service for creating, verifying, and decoding JWT access tokens."""

    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    @classmethod
    def create_access_token(cls, subject: str) -> str:
        """Create a JWT access token containing only 'sub' and 'exp' claims.

        Args:
            subject: The subject identification (e.g., username, email, or user ID).

        Returns:
            The encoded JWT token string.
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Payload must contain ONLY 'sub' and 'exp'
        payload = {
            "sub": subject,
            "exp": expire
        }
        
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def verify_access_token(cls, token: str) -> dict:
        """Verify signature, claims, and expiration of a JWT access token.

        Args:
            token: The JWT token to verify.

        Returns:
            The decoded payload dictionary.

        Raises:
            TokenExpiredError: If the token's expiration date has passed.
            TokenInvalidError: If the token is invalid, malformed, or has incorrect claims.
        """
        try:
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            if "sub" not in payload:
                raise TokenInvalidError("Missing subject claim ('sub') in JWT payload")
            return payload
        except ExpiredSignatureError as e:
            raise TokenExpiredError("Token signature has expired") from e
        except JWTError as e:
            raise TokenInvalidError("Token signature or format is invalid") from e

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        """Decode a JWT access token without verifying its expiration.

        This method verifies the cryptographic signature but does not check expiration,
        which is useful for inspecting claims of expired tokens.

        Args:
            token: The JWT token to decode.

        Returns:
            The decoded payload dictionary.

        Raises:
            TokenInvalidError: If the token signature is invalid, malformed, or missing claims.
        """
        try:
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM],
                options={"verify_exp": False}
            )
            if "sub" not in payload:
                raise TokenInvalidError("Missing subject claim ('sub') in JWT payload")
            return payload
        except JWTError as e:
            raise TokenInvalidError("Token signature or format is invalid") from e
