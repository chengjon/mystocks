"""
Multi-Factor Authentication (MFA) Implementation

Task 2.1 Phase 3: Multi-Factor Authentication Support
Supports TOTP, Email OTP, and SMS verification
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import logging
import secrets
import string
import qrcode
import io
import base64
import pyotp

from app.core.config import settings

logger = logging.getLogger(__name__)


class MFAProvider(ABC):
    """
    Abstract base class for MFA providers

    Defines interface for all MFA methods (TOTP, Email, SMS)
    """

    @abstractmethod
    async def setup(self, user_id: int, user_email: str) -> Dict[str, Any]:
        """Setup MFA for user"""
        pass

    @abstractmethod
    async def verify(self, user_id: int, code: str) -> bool:
        """Verify MFA code"""
        pass

    @abstractmethod
    async def disable(self, user_id: int) -> bool:
        """Disable MFA"""
        pass


class TOTPProvider(MFAProvider):
    """
    Time-based One-Time Password (TOTP) provider

    Uses pyotp library for industry-standard TOTP implementation
    Compatible with Google Authenticator, Microsoft Authenticator, Authy, etc.
    """

    def __init__(self):
        self.issuer = settings.mfa_totp_issuer
        self.backup_codes_count = 10

    async def setup(self, user_id: int, user_email: str) -> Dict[str, Any]:
        """
        Setup TOTP for user

        Args:
            user_id: User ID
            user_email: User email address

        Returns:
            Dictionary with:
            - secret: Base32-encoded TOTP secret
            - qr_code: Data URL for QR code image
            - backup_codes: List of backup codes
        """
        # Generate TOTP secret
        secret = pyotp.random_base32()

        # Create TOTP instance
        totp = pyotp.TOTP(secret)

        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(
            name=user_email, issuer_name=self.issuer
        )

        # Generate QR code
        qr_code_image = self._generate_qr_code(provisioning_uri)

        # Generate backup codes
        backup_codes = self._generate_backup_codes()

        logger.info(f"TOTP setup initiated for user: {user_id}")

        return {
            "method": "totp",
            "secret": secret,
            "qr_code": qr_code_image,
            "backup_codes": backup_codes,
            "manual_entry_key": secret,  # For manual entry if QR doesn't work
        }

    async def verify(self, secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code

        Args:
            secret: TOTP secret
            code: 6-digit TOTP code
            window: Time window in steps (default 1 = ±30 seconds)

        Returns:
            True if code is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            # Verify with time window tolerance
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.warning(f"TOTP verification failed: {e}")
            return False

    async def disable(self, user_id: int) -> bool:
        """Disable TOTP for user"""
        logger.info(f"TOTP disabled for user: {user_id}")
        return True

    def _generate_qr_code(self, provisioning_uri: str) -> str:
        """
        Generate QR code image

        Args:
            provisioning_uri: TOTP provisioning URI

        Returns:
            Data URL for QR code image (PNG, base64-encoded)
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Generate PIL image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f"data:image/png;base64,{img_base64}"

    def _generate_backup_codes(self) -> List[str]:
        """
        Generate backup codes

        Returns:
            List of 10 backup codes (8 characters each, alphanumeric)
        """
        codes = []
        characters = string.ascii_uppercase + string.digits

        for _ in range(self.backup_codes_count):
            code = "".join(secrets.choice(characters) for _ in range(8))
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)

        return codes

    def verify_backup_code(
        self, backup_codes: List[str], provided_code: str
    ) -> Tuple[bool, List[str]]:
        """
        Verify backup code and remove it from the list

        Args:
            backup_codes: List of remaining backup codes
            provided_code: Backup code provided by user

        Returns:
            Tuple of (is_valid, remaining_codes)
        """
        # Normalize provided code (remove hyphens, convert to uppercase)
        normalized_provided = provided_code.replace("-", "").upper()

        for i, code in enumerate(backup_codes):
            normalized_stored = code.replace("-", "").upper()
            if normalized_provided == normalized_stored:
                # Remove used code
                remaining = backup_codes[:i] + backup_codes[i + 1 :]
                logger.info("Backup code used and removed")
                return True, remaining

        logger.warning("Invalid backup code provided")
        return False, backup_codes


class EmailOTPProvider(MFAProvider):
    """
    Email-based One-Time Password (OTP) provider

    Sends 6-digit code via email for verification
    """

    def __init__(self):
        self.code_length = settings.mfa_email_code_length
        self.code_expires_minutes = settings.mfa_email_code_expires_minutes

    async def setup(self, user_id: int, user_email: str) -> Dict[str, Any]:
        """
        Setup Email OTP for user

        Args:
            user_id: User ID
            user_email: User email address

        Returns:
            Dictionary with setup confirmation
        """
        logger.info(f"Email OTP setup initiated for user: {user_id}")

        return {
            "method": "email",
            "email": user_email,
            "message": f"Verification codes will be sent to {user_email}",
        }

    async def generate_code(self) -> Tuple[str, datetime]:
        """
        Generate OTP code

        Returns:
            Tuple of (code, expiration_time)
        """
        code = "".join(secrets.choice(string.digits) for _ in range(self.code_length))
        expiration = datetime.utcnow() + timedelta(minutes=self.code_expires_minutes)

        return code, expiration

    async def verify(
        self, stored_code: str, provided_code: str, expiration: datetime
    ) -> bool:
        """
        Verify OTP code

        Args:
            stored_code: Code stored in database
            provided_code: Code provided by user
            expiration: Code expiration time

        Returns:
            True if code is valid and not expired
        """
        # Check if code has expired
        if datetime.utcnow() > expiration:
            logger.warning("OTP code has expired")
            return False

        # Check if code matches
        if stored_code == provided_code:
            logger.info("OTP code verified successfully")
            return True

        logger.warning("OTP code does not match")
        return False

    async def disable(self, user_id: int) -> bool:
        """Disable Email OTP for user"""
        logger.info(f"Email OTP disabled for user: {user_id}")
        return True


class SMSProvider(MFAProvider):
    """
    SMS-based One-Time Password provider

    Sends 6-digit code via SMS for verification
    (Optional implementation - placeholder for future SMS service integration)
    """

    def __init__(self):
        self.code_length = settings.mfa_email_code_length
        self.code_expires_minutes = settings.mfa_email_code_expires_minutes

    async def setup(self, user_id: int, user_phone: str) -> Dict[str, Any]:
        """
        Setup SMS OTP for user

        Args:
            user_id: User ID
            user_phone: User phone number

        Returns:
            Dictionary with setup confirmation
        """
        logger.info(f"SMS OTP setup initiated for user: {user_id}")

        return {
            "method": "sms",
            "phone": self._mask_phone(user_phone),
            "message": f"Verification codes will be sent to {self._mask_phone(user_phone)}",
        }

    async def generate_code(self) -> Tuple[str, datetime]:
        """
        Generate OTP code

        Returns:
            Tuple of (code, expiration_time)
        """
        code = "".join(secrets.choice(string.digits) for _ in range(self.code_length))
        expiration = datetime.utcnow() + timedelta(minutes=self.code_expires_minutes)

        return code, expiration

    async def verify(
        self, stored_code: str, provided_code: str, expiration: datetime
    ) -> bool:
        """
        Verify OTP code

        Args:
            stored_code: Code stored in database
            provided_code: Code provided by user
            expiration: Code expiration time

        Returns:
            True if code is valid and not expired
        """
        # Check if code has expired
        if datetime.utcnow() > expiration:
            logger.warning("SMS OTP code has expired")
            return False

        # Check if code matches
        if stored_code == provided_code:
            logger.info("SMS OTP code verified successfully")
            return True

        logger.warning("SMS OTP code does not match")
        return False

    async def disable(self, user_id: int) -> bool:
        """Disable SMS OTP for user"""
        logger.info(f"SMS OTP disabled for user: {user_id}")
        return True

    @staticmethod
    def _mask_phone(phone: str) -> str:
        """Mask phone number for display"""
        if len(phone) < 4:
            return "***"
        return f"***{phone[-4:]}"


class MFAProviderFactory:
    """
    MFA Provider Factory

    Creates and manages MFA provider instances
    """

    _providers = {
        "totp": TOTPProvider,
        "email": EmailOTPProvider,
        "sms": SMSProvider,
    }

    @classmethod
    def get_provider(cls, method: str) -> Optional[MFAProvider]:
        """
        Get MFA provider by method

        Args:
            method: MFA method name ('totp', 'email', 'sms')

        Returns:
            MFA provider instance or None
        """
        provider_class = cls._providers.get(method.lower())
        if not provider_class:
            logger.warning(f"MFA provider '{method}' not found")
            return None

        return provider_class()

    @classmethod
    def get_available_methods(cls) -> List[str]:
        """Get list of available MFA methods"""
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register custom MFA provider

        Args:
            name: Provider name
            provider_class: Provider class
        """
        cls._providers[name.lower()] = provider_class
