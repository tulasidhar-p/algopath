import bcrypt

class PasswordService:
    """Stateless utility service for password hashing and verification.

    This service is completely decoupled from database models and framework dependencies.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using bcrypt.

        Args:
            password: The plaintext password to hash.

        Returns:
            The hashed password as a string.
        """
        salt = bcrypt.gensalt()
        hashed_payload = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_payload.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash.

        Args:
            password: The plaintext password to verify.
            hashed_password: The bcrypt hash to verify against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), 
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False
