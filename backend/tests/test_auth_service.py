import pytest
from unittest.mock import patch
from app.services.auth_service import (
    AuthService, 
    UserAlreadyExistsError, 
    InvalidCredentialsError, 
    UserNotFoundError,
    AuthenticationError
)
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.models.user import User, UserTopicProgress
from app.repositories import user_repo

def test_register_user_success(db_session, seeded_topics):
    register_data = RegisterRequest(
        name="John Doe",
        email="  John.Doe@Example.Com  ",
        password="securepassword123"
    )
    
    # 1. Successful registration
    response = AuthService.register_user(db_session, register_data)
    
    # 2. Check return type and content
    assert isinstance(response, UserResponse)
    assert response.name == "John Doe"
    assert response.email == "john.doe@example.com"  # normalized
    assert not hasattr(response, "password")
    assert not hasattr(response, "hashed_password")
    
    # 3. Check DB existence
    db_user = db_session.query(User).filter(User.email == "john.doe@example.com").first()
    assert db_user is not None
    assert db_user.name == "John Doe"
    
    # 4. Check topic progress initialization
    progress_records = db_session.query(UserTopicProgress).filter(UserTopicProgress.user_id == db_user.id).all()
    assert len(progress_records) == 2
    
    # First topic (arrays) should be unlocked, second topic (two-pointers) locked
    arrays_progress = next(p for p in progress_records if p.topic.slug == "arrays")
    twopointers_progress = next(p for p in progress_records if p.topic.slug == "two-pointers")
    assert arrays_progress.is_unlocked is True
    assert twopointers_progress.is_unlocked is False

def test_register_user_duplicate_email(db_session, seeded_topics):
    register_data = RegisterRequest(
        name="John Doe",
        email="john@example.com",
        password="securepassword123"
    )
    AuthService.register_user(db_session, register_data)
    
    # Attempting to register the same email (even with different capitalization/whitespace) should fail
    duplicate_data = RegisterRequest(
        name="John Second",
        email=" JOHN@EXAMPLE.COM ",
        password="password987"
    )
    
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        AuthService.register_user(db_session, duplicate_data)
    assert "already exists" in str(exc_info.value)

def test_register_user_database_error_triggers_rollback(db_session, seeded_topics):
    register_data = RegisterRequest(
        name="Failure Test",
        email="fail@example.com",
        password="securepassword123"
    )
    
    # Mock user_repo.initialize_user_topic_progress to fail and check rollback
    with patch.object(user_repo, "initialize_user_topic_progress", side_effect=Exception("Database issue")):
        with pytest.raises(AuthenticationError):
            AuthService.register_user(db_session, register_data)
            
    # Verify user record is NOT in the database due to transaction rollback
    db_user = db_session.query(User).filter(User.email == "fail@example.com").first()
    assert db_user is None

def test_login_user_success(db_session, seeded_topics):
    # Register user first
    register_data = RegisterRequest(
        name="Login User",
        email="login@example.com",
        password="mysecurepassword"
    )
    AuthService.register_user(db_session, register_data)
    
    # Login request
    login_data = LoginRequest(
        email="  LOGIN@EXAMPLE.COM  ",  # with spaces and caps to test normalization
        password="mysecurepassword"
    )
    
    response = AuthService.login_user(db_session, login_data)
    
    assert isinstance(response, TokenResponse)
    assert response.access_token != ""
    assert response.token_type == "bearer"

def test_login_user_invalid_credentials(db_session, seeded_topics):
    # Register a user
    register_data = RegisterRequest(
        name="Mock User",
        email="mock@example.com",
        password="goodpassword"
    )
    AuthService.register_user(db_session, register_data)
    
    # 1. Invalid email
    login_invalid_email = LoginRequest(email="nonexistent@example.com", password="goodpassword")
    with pytest.raises(InvalidCredentialsError) as exc_info_email:
        AuthService.login_user(db_session, login_invalid_email)
    
    # 2. Invalid password
    login_invalid_password = LoginRequest(email="mock@example.com", password="wrongpassword")
    with pytest.raises(InvalidCredentialsError) as exc_info_pwd:
        AuthService.login_user(db_session, login_invalid_password)
        
    # Security requirement: both errors must be identical
    assert str(exc_info_email.value) == str(exc_info_pwd.value)
    assert "Invalid email or password" in str(exc_info_email.value)

def test_get_user_by_email(db_session, seeded_topics):
    # Register a user
    register_data = RegisterRequest(
        name="Search User",
        email="search@example.com",
        password="password123"
    )
    AuthService.register_user(db_session, register_data)
    
    # 1. Retrieve successfully
    user = AuthService.get_user_by_email(db_session, "  SEARCH@EXAMPLE.COM  ")
    assert isinstance(user, User)
    assert user.name == "Search User"
    assert user.email == "search@example.com"
    
    # 2. Non-existent email raises UserNotFoundError
    with pytest.raises(UserNotFoundError):
        AuthService.get_user_by_email(db_session, "unknown@example.com")

def test_get_user_by_id(db_session, seeded_topics):
    # Register a user
    register_data = RegisterRequest(
        name="Id Search User",
        email="idsearch@example.com",
        password="password123"
    )
    response = AuthService.register_user(db_session, register_data)
    
    # 1. Retrieve successfully
    user = AuthService.get_user_by_id(db_session, response.id)
    assert isinstance(user, User)
    assert user.name == "Id Search User"
    assert user.email == "idsearch@example.com"
    
    # 2. Non-existent ID raises UserNotFoundError
    with pytest.raises(UserNotFoundError):
        AuthService.get_user_by_id(db_session, 99999)
