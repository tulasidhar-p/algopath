from app.services.password_service import PasswordService

def test_hash_password_success():
    password = "supersecretpassword123"
    hashed = PasswordService.hash_password(password)
    assert hashed != password
    assert len(hashed) > 0
    # BCrypt hashes standardly start with $2a$, $2b$, or $2y$
    assert hashed.startswith("$2")

def test_verify_password_correct():
    password = "mypassword"
    hashed = PasswordService.hash_password(password)
    assert PasswordService.verify_password(password, hashed) is True

def test_verify_password_incorrect():
    password = "mypassword"
    hashed = PasswordService.hash_password(password)
    assert PasswordService.verify_password("wrongpassword", hashed) is False

def test_verify_password_invalid_hash():
    # Handles malformed hash format gracefully without crashing
    assert PasswordService.verify_password("password", "invalidhash") is False
    assert PasswordService.verify_password("password", "") is False
