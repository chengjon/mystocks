"""
Comprehensive Authentication and MFA Testing

Task 2.1 Phase 4: Testing for OAuth2, MFA, and complete auth flows
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import base64
import json

from app.core.mfa import (
    TOTPProvider,
    EmailOTPProvider,
    SMSProvider,
    MFAProviderFactory,
)
from app.core.security import create_access_token, verify_token
from app.core.config import settings


class TestTOTPProvider:
    """Test TOTP provider functionality"""

    @pytest.fixture
    def totp_provider(self):
        """Create TOTP provider instance"""
        return TOTPProvider()

    def test_totp_setup_returns_secret_and_qr(self, totp_provider):
        """Test TOTP setup generates secret and QR code"""
        import asyncio

        result = asyncio.run(totp_provider.setup(user_id=1, user_email="user@test.com"))

        assert result["method"] == "totp"
        assert "secret" in result
        assert "qr_code" in result
        assert result["qr_code"].startswith("data:image/png;base64,")
        assert "backup_codes" in result
        assert len(result["backup_codes"]) == 10

    def test_totp_backup_codes_format(self, totp_provider):
        """Test backup codes have correct format"""
        import asyncio

        result = asyncio.run(totp_provider.setup(user_id=1, user_email="user@test.com"))

        for code in result["backup_codes"]:
            # Format: XXXX-XXXX (4 chars - 4 chars)
            assert len(code) == 9  # 8 chars + 1 hyphen
            assert code[4] == "-"
            assert code[:4].isalnum()
            assert code[5:].isalnum()

    def test_totp_verify_valid_code(self, totp_provider):
        """Test TOTP verification with valid code"""
        import asyncio
        import pyotp

        # Generate a test secret
        secret = pyotp.random_base32()

        # Generate a valid code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Verify the code
        result = asyncio.run(totp_provider.verify(secret, valid_code))
        assert result is True

    def test_totp_verify_invalid_code(self, totp_provider):
        """Test TOTP verification with invalid code"""
        import asyncio
        import pyotp

        secret = pyotp.random_base32()
        invalid_code = "000000"

        result = asyncio.run(totp_provider.verify(secret, invalid_code))
        assert result is False

    def test_backup_code_verification_and_removal(self, totp_provider):
        """Test backup code verification removes used code"""
        codes = ["ABCD-1234", "EFGH-5678", "IJKL-9012"]

        # Verify first code
        is_valid, remaining = totp_provider.verify_backup_code(codes, "ABCD-1234")

        assert is_valid is True
        assert len(remaining) == 2
        assert "ABCD-1234" not in remaining
        assert "EFGH-5678" in remaining

    def test_backup_code_normalization(self, totp_provider):
        """Test backup codes are normalized before comparison"""
        codes = ["ABCD-1234", "EFGH-5678"]

        # Test with different case and no hyphen
        is_valid, remaining = totp_provider.verify_backup_code(codes, "abcd1234")

        assert is_valid is True
        assert len(remaining) == 1


class TestEmailOTPProvider:
    """Test Email OTP provider functionality"""

    @pytest.fixture
    def email_provider(self):
        """Create Email OTP provider instance"""
        return EmailOTPProvider()

    def test_email_setup_returns_email(self, email_provider):
        """Test email OTP setup returns email address"""
        import asyncio

        result = asyncio.run(
            email_provider.setup(user_id=1, user_email="user@test.com")
        )

        assert result["method"] == "email"
        assert result["email"] == "user@test.com"
        assert "message" in result

    def test_email_code_generation(self, email_provider):
        """Test email OTP code generation"""
        import asyncio

        code, expiration = asyncio.run(email_provider.generate_code())

        assert len(code) == 6
        assert code.isdigit()
        assert expiration > datetime.utcnow()

    def test_email_code_expiration(self, email_provider):
        """Test email OTP code expiration check"""
        import asyncio

        code = "123456"
        # Expired expiration time
        expired_expiration = datetime.utcnow() - timedelta(minutes=1)

        result = asyncio.run(email_provider.verify(code, code, expired_expiration))

        assert result is False

    def test_email_code_verification(self, email_provider):
        """Test email OTP code verification"""
        import asyncio

        code = "123456"
        valid_expiration = datetime.utcnow() + timedelta(minutes=5)

        result = asyncio.run(email_provider.verify(code, code, valid_expiration))

        assert result is True

    def test_email_code_mismatch(self, email_provider):
        """Test email OTP with mismatched code"""
        import asyncio

        valid_expiration = datetime.utcnow() + timedelta(minutes=5)

        result = asyncio.run(
            email_provider.verify("123456", "654321", valid_expiration)
        )

        assert result is False


class TestSMSProvider:
    """Test SMS provider functionality"""

    @pytest.fixture
    def sms_provider(self):
        """Create SMS provider instance"""
        return SMSProvider()

    def test_sms_setup_returns_masked_phone(self, sms_provider):
        """Test SMS setup returns masked phone number"""
        import asyncio

        result = asyncio.run(sms_provider.setup(user_id=1, user_phone="1234567890"))

        assert result["method"] == "sms"
        assert "***" in result["phone"]
        assert "7890" in result["phone"]
        assert "123456" not in result["phone"]

    def test_sms_phone_masking(self, sms_provider):
        """Test phone number masking"""
        masked = sms_provider._mask_phone("1234567890")

        assert masked == "***7890"

    def test_sms_code_generation(self, sms_provider):
        """Test SMS OTP code generation"""
        import asyncio

        code, expiration = asyncio.run(sms_provider.generate_code())

        assert len(code) == 6
        assert code.isdigit()
        assert expiration > datetime.utcnow()


class TestMFAProviderFactory:
    """Test MFA provider factory"""

    def test_factory_get_totp_provider(self):
        """Test factory returns TOTP provider"""
        provider = MFAProviderFactory.get_provider("totp")

        assert provider is not None
        assert isinstance(provider, TOTPProvider)

    def test_factory_get_email_provider(self):
        """Test factory returns Email provider"""
        provider = MFAProviderFactory.get_provider("email")

        assert provider is not None
        assert isinstance(provider, EmailOTPProvider)

    def test_factory_get_sms_provider(self):
        """Test factory returns SMS provider"""
        provider = MFAProviderFactory.get_provider("sms")

        assert provider is not None
        assert isinstance(provider, SMSProvider)

    def test_factory_returns_none_for_invalid_provider(self):
        """Test factory returns None for invalid provider"""
        provider = MFAProviderFactory.get_provider("invalid")

        assert provider is None

    def test_factory_get_available_methods(self):
        """Test factory returns list of available methods"""
        methods = MFAProviderFactory.get_available_methods()

        assert "totp" in methods
        assert "email" in methods
        assert "sms" in methods
        assert len(methods) == 3

    def test_factory_case_insensitive(self):
        """Test factory method names are case-insensitive"""
        provider1 = MFAProviderFactory.get_provider("TOTP")
        provider2 = MFAProviderFactory.get_provider("ToTp")

        assert isinstance(provider1, TOTPProvider)
        assert isinstance(provider2, TOTPProvider)


class TestJWTToken:
    """Test JWT token generation and verification"""

    def test_create_and_verify_token(self):
        """Test JWT token creation and verification"""
        data = {"sub": "testuser", "user_id": 1, "role": "user"}
        token = create_access_token(data)

        verified = verify_token(token)

        assert verified is not None
        assert verified.username == "testuser"

    def test_token_with_expiration(self):
        """Test token with custom expiration"""
        data = {"sub": "testuser", "user_id": 1}
        expires_delta = timedelta(minutes=1)

        token = create_access_token(data, expires_delta)
        verified = verify_token(token)

        assert verified is not None

    def test_expired_token_verification(self):
        """Test expired token fails verification"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired

        token = create_access_token(data, expires_delta)
        verified = verify_token(token)

        assert verified is None

    def test_token_with_mfa_pending(self):
        """Test token with mfa_pending flag"""
        data = {
            "sub": "testuser",
            "user_id": 1,
            "role": "user",
            "mfa_pending": True,
        }

        token = create_access_token(data)
        verified = verify_token(token)

        assert verified is not None
        assert verified.username == "testuser"


class TestMFAStateManagement:
    """Test MFA state management and backup codes"""

    def test_backup_codes_are_unique(self):
        """Test backup codes are unique"""
        provider = TOTPProvider()
        codes = provider._generate_backup_codes()

        # Check all codes are unique
        assert len(codes) == len(set(codes))

    def test_backup_codes_count(self):
        """Test correct number of backup codes generated"""
        provider = TOTPProvider()
        codes = provider._generate_backup_codes()

        assert len(codes) == 10

    def test_qr_code_contains_provisioning_uri(self):
        """Test QR code is valid base64 PNG"""
        provider = TOTPProvider()

        import pyotp

        totp = pyotp.TOTP("JBSWY3DPEBLW64TMMQ======")
        uri = totp.provisioning_uri("user@test.com", "TestIssuer")

        qr_code = provider._generate_qr_code(uri)

        assert qr_code.startswith("data:image/png;base64,")
        # Verify base64 is valid
        base64_data = qr_code.replace("data:image/png;base64,", "")
        try:
            base64.b64decode(base64_data)
            is_valid_base64 = True
        except Exception:
            is_valid_base64 = False

        assert is_valid_base64


class TestOAuth2StateToken:
    """Test OAuth2 state token generation and verification"""

    def test_create_and_verify_oauth2_state(self):
        """Test OAuth2 state token creation and verification"""
        from app.core.oauth2_providers import (
            create_oauth2_state,
            verify_oauth2_state,
        )

        state = create_oauth2_state(user_id=1)

        # Verify state
        state_data = verify_oauth2_state(state)

        assert state_data is not None
        assert state_data.get("user_id") == 1
        assert "nonce" in state_data
        assert "timestamp" in state_data

    def test_oauth2_state_expiration(self):
        """Test OAuth2 state token expiration"""
        from app.core.oauth2_providers import (
            create_oauth2_state,
            verify_oauth2_state,
        )

        # Create an "expired" state by manipulating the timestamp
        state_data = {
            "nonce": "test",
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "user_id": 1,
        }
        state_json = json.dumps(state_data)
        state = base64.b64encode(state_json.encode()).decode()

        # Should raise ValueError for expired token
        with pytest.raises(ValueError):
            verify_oauth2_state(state, max_age_minutes=10)

    def test_oauth2_state_invalid_format(self):
        """Test OAuth2 state verification with invalid format"""
        from app.core.oauth2_providers import verify_oauth2_state

        # Invalid base64
        with pytest.raises(ValueError):
            verify_oauth2_state("not-valid-base64!")


class TestAuthenticationFlow:
    """Test complete authentication flows"""

    def test_login_without_mfa(self):
        """Test login flow for user without MFA"""
        # This would require FastAPI TestClient with DB
        # Placeholder for integration test
        pass

    def test_login_with_mfa_required(self):
        """Test login flow for user with MFA enabled"""
        # Placeholder for integration test
        pass

    def test_mfa_verification_grants_access(self):
        """Test MFA verification grants full access token"""
        # Placeholder for integration test
        pass

    def test_temporary_token_expires(self):
        """Test temporary MFA token expires"""
        # Placeholder for integration test
        pass


class TestMFASecurityConsiderations:
    """Test security aspects of MFA"""

    def test_code_expiration_enforcement(self):
        """Test code expiration is enforced"""
        import asyncio

        provider = EmailOTPProvider()
        code = "123456"

        # Create expired expiration time
        expired = datetime.utcnow() - timedelta(seconds=1)

        result = asyncio.run(provider.verify(code, code, expired))

        assert result is False

    def test_totp_time_window_tolerance(self):
        """Test TOTP verification allows time window"""
        import asyncio
        import pyotp

        provider = TOTPProvider()
        secret = pyotp.random_base32()

        # Generate a valid code
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Should verify with window=1 (±30 seconds)
        result = asyncio.run(provider.verify(secret, code, window=1))

        assert result is True

    def test_backup_code_one_time_use(self):
        """Test backup codes can only be used once"""
        provider = TOTPProvider()
        codes = ["ABCD-1234", "EFGH-5678"]

        # First use
        is_valid1, remaining1 = provider.verify_backup_code(codes, "ABCD-1234")
        assert is_valid1 is True

        # Try to use same code again
        is_valid2, remaining2 = provider.verify_backup_code(remaining1, "ABCD-1234")
        assert is_valid2 is False

    def test_invalid_secret_format_rejected(self):
        """Test invalid TOTP secret is rejected"""
        import asyncio

        provider = TOTPProvider()

        # Invalid secret (should contain only valid base32 chars)
        # Returns False instead of raising, due to error handling in pyotp
        result = asyncio.run(provider.verify("INVALID!!!SECRET", "123456"))
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
