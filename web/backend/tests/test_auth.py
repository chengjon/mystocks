"""
Authentication API Unit Tests

Tests for JWT authentication system including:
- User registration
- User login
- Token refresh
- Password reset
- User validation
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
)


# PostgreSQL test database
TEST_DATABASE_URL = (
    "postgresql+psycopg2://postgres:c790414J@192.168.123.104:5438/mystocks_test"
)


@pytest.fixture
def test_db():
    """Create PostgreSQL test database session with transaction rollback isolation"""
    engine = create_engine(TEST_DATABASE_URL)
    connection = engine.connect()

    # Start a top-level transaction that will be rolled back after each test
    transaction = connection.begin()

    # Bind session to the connection (shares the same transaction)
    Session = sessionmaker(bind=connection)
    session = Session()

    # Clean test data before each test (within the transaction)
    session.execute(text("DELETE FROM user_audit_log"))
    session.execute(text("DELETE FROM password_reset_tokens"))
    session.execute(text("DELETE FROM users"))
    session.flush()

    # Override commit/close/rollback to use savepoints instead of real commits
    # This prevents the auth routes from committing the outer transaction
    _orig_commit = session.commit
    _orig_close = session.close
    _orig_rollback = session.rollback

    def _fake_commit():
        session.flush()  # Flush to DB but don't commit the outer transaction

    def _fake_close():
        pass  # Don't close - we manage the lifecycle

    def _fake_rollback():
        pass  # Don't rollback - we manage the lifecycle

    session.commit = _fake_commit
    session.close = _fake_close
    session.rollback = _fake_rollback

    try:
        yield session
    finally:
        session.commit = _orig_commit
        session.close = _orig_close
        session.rollback = _orig_rollback
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture
def client(test_db):
    """Create test client with PostgreSQL test database"""
    from app.core.config import settings

    # Disable CSRF for tests (without enabling testing mode which uses mock auth)
    original_csrf = settings.csrf_enabled
    settings.csrf_enabled = False

    # Mock get_postgresql_session to return the test session (with transaction rollback)
    with patch("app.core.database.get_postgresql_session", side_effect=lambda: test_db):
        yield TestClient(app)

    settings.csrf_enabled = original_csrf


class TestPasswordSecurity:
    """Test password hashing and verification"""

    def test_password_hashing(self):
        """Test password hashing generates different hashes for same password"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_password_verification(self):
        """Test password verification"""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True

        # Wrong password should not verify
        assert verify_password("WrongPassword123", hashed) is False

    def test_password_hash_length_limit(self):
        """Test bcrypt password length limit (72 bytes)"""
        # Bcrypt has a 72-byte limit
        long_password = "a" * 100  # 100 characters
        hashed = get_password_hash(long_password)

        # Should be truncated to 72 bytes but still work
        assert verify_password(long_password, hashed) is True


class TestJWTToken:
    """Test JWT token generation and verification"""

    def test_create_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser", "user_id": 1, "role": "user"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        """Test verification of valid token"""
        data = {"sub": "testuser", "user_id": 1, "role": "admin"}
        token = create_access_token(data)
        token_data = verify_token(token)

        assert token_data is not None
        assert token_data.username == "testuser"
        assert token_data.user_id == 1
        assert token_data.role == "admin"

    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        token_data = verify_token(invalid_token)

        assert token_data is None

    def test_verify_expired_token(self):
        """Test verification of expired token"""
        from datetime import timedelta

        # Create token that expired 1 hour ago
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data, expires_delta=timedelta(hours=-1))

        token_data = verify_token(token)
        assert token_data is None


class TestUserRegistration:
    """Test user registration API"""

    def test_register_user_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123",
                "role": "user",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data.get("success") is True or data.get("code") == "SUCCESS"
        assert data["data"]["username"] == "testuser"
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["role"] == "user"
        assert "id" in data["data"]
        # Password should not be in response
        assert "password" not in data["data"]
        assert "hashed_password" not in data["data"]

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "TestPass123",
            },
        )

        # Second registration with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        body = response.json()
        error_msg = body.get("detail", body.get("message", "")).lower()
        assert "already exists" in error_msg

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser1",
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        # Second registration with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser2",
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        body = response.json()
        error_msg = body.get("detail", body.get("message", "")).lower()
        assert "already exists" in error_msg

    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak",  # Too short, no uppercase, no digit
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",  # Invalid email format
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_username(self, client):
        """Test registration with short username"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",  # Less than 3 characters
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login API"""

    def test_login_success(self, client):
        """Test successful user login"""
        # First register a user
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        # Then login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("success") is True or data.get("code") == "SUCCESS"
        assert "token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "expires_in" in data["data"]
        assert data["data"]["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client):
        """Test login with wrong password"""
        # Register a user
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """Test token refresh API"""

    def test_refresh_token_success(self, client):
        """Test successful token refresh"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123",
            },
        )
        token = login_response.json()["data"]["token"]

        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid_auth(self, client):
        """Test token refresh with invalid authorization"""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordReset:
    """Test password reset API"""

    def test_request_password_reset(self, client):
        """Test password reset request"""
        response = client.post(
            "/api/v1/auth/reset-password/request",
            json={"email": "test@example.com"},
        )

        # Should always return success (to prevent email enumeration)
        assert response.status_code == status.HTTP_200_OK
        assert "sent" in response.json()["message"].lower()

    def test_confirm_password_reset_success(self, client):
        """Test successful password reset confirmation"""
        # Register a user
        reg_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "OldPassword123",
            },
        )
        # Get actual user_id from registration response
        user_id = reg_response.json()["data"]["id"]

        # Request reset (this would normally send email with token)
        # For testing, we'll create a reset token manually
        from app.core.security import create_access_token
        from datetime import timedelta

        reset_token = create_access_token(
            data={"sub": "testuser", "user_id": user_id, "role": "user", "purpose": "password_reset"},
            expires_delta=timedelta(hours=1),
        )

        # Confirm reset
        response = client.post(
            "/api/v1/auth/reset-password/confirm",
            json={
                "token": reset_token,
                "new_password": "NewPassword123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.json()["message"].lower()

        # Verify old password no longer works
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "OldPassword123",
            },
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED

        # Verify new password works
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "NewPassword123",
            },
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_confirm_password_reset_invalid_token(self, client):
        """Test password reset with invalid token"""
        response = client.post(
            "/api/v1/auth/reset-password/confirm",
            json={
                "token": "invalid_token",
                "new_password": "NewPassword123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetCurrentUser:
    """Test get current user API"""

    def test_get_current_user_success(self, client):
        """Test getting current user info"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123",
            },
        )
        token = login_response.json()["data"]["token"]

        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"

    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCSRFToken:
    """Test CSRF token API"""

    def test_get_csrf_token(self, client):
        """Test getting CSRF token"""
        response = client.get("/api/v1/auth/csrf/token")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("success") is True or data.get("code") == "SUCCESS"
        assert "token" in data["data"]
        assert data["data"]["token_type"] == "csrf"
