"""
Encryption utilities for protecting sensitive data
Task 1.3: Sensitive Data Encryption

Provides AES-256-GCM encryption for:
- Database passwords and connection strings
- API keys and tokens
- User credentials
- Configuration secrets
"""

import os
import base64
import json
from typing import Union, Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

logger = structlog.get_logger()


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data using AES-256-GCM

    SECURITY: All sensitive data should be encrypted at rest using this manager.
    Encryption keys are derived from master password using PBKDF2.
    """

    def __init__(self, master_password: str = None):
        """
        Initialize encryption manager with master password

        Args:
            master_password: Master password for deriving encryption keys.
                           If not provided, uses ENCRYPTION_MASTER_PASSWORD env var

        SECURITY: Master password should be stored securely in environment
        """
        if master_password is None:
            master_password = os.getenv("ENCRYPTION_MASTER_PASSWORD")
            if not master_password:
                logger.warning(
                    "⚠️ No encryption master password provided. "
                    "Using insecure default. Set ENCRYPTION_MASTER_PASSWORD in production!"
                )
                master_password = "default-insecure-password-change-me"

        self.master_password = master_password
        self._cipher_key = None
        self._setup_key()

    def _setup_key(self):
        """Derive encryption key from master password using PBKDF2"""
        # Use a fixed salt for consistent key derivation
        # SECURITY: In production, this should be configurable per instance
        salt = b"mystocks-encryption-salt-v1"

        # Derive 32-byte key (256 bits) for AES-256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        self._cipher_key = kdf.derive(self.master_password.encode())
        logger.info("✅ Encryption key derived from master password")

    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """
        Encrypt plaintext using AES-256-GCM

        Args:
            plaintext: Data to encrypt (str or bytes)

        Returns:
            Base64-encoded encrypted data with IV and tag prepended

        Format: base64(nonce + ciphertext + tag)
        """
        # Convert to bytes if string
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")

        # Generate random nonce (96 bits / 12 bytes for GCM)
        nonce = os.urandom(12)

        # Create cipher and encrypt
        cipher = AESGCM(self._cipher_key)
        ciphertext = cipher.encrypt(nonce, plaintext, None)

        # Combine nonce + ciphertext (which includes auth tag)
        encrypted_data = nonce + ciphertext

        # Return base64-encoded result
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt AES-256-GCM encrypted data

        Args:
            encrypted_data: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext as string

        Raises:
            ValueError: If decryption fails (tampered data or wrong key)
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)

            # Extract nonce (first 12 bytes) and ciphertext (remainder)
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]

            # Decrypt
            cipher = AESGCM(self._cipher_key)
            plaintext = cipher.decrypt(nonce, ciphertext, None)

            return plaintext.decode("utf-8")

        except Exception as e:
            logger.error("❌ Decryption failed", error=str(e))
            raise ValueError(f"Failed to decrypt data: {str(e)}")

    def encrypt_dict(self, data: Dict[str, Any], keys_to_encrypt: list) -> Dict:
        """
        Encrypt specific keys in a dictionary

        Args:
            data: Dictionary containing sensitive data
            keys_to_encrypt: List of key names to encrypt

        Returns:
            Dictionary with specified keys encrypted
        """
        encrypted_data = data.copy()

        for key in keys_to_encrypt:
            if key in encrypted_data:
                value = encrypted_data[key]
                if value is not None:
                    # Mark encrypted values with __encrypted__ prefix
                    encrypted_data[f"{key}__encrypted__"] = self.encrypt(
                        str(value)
                    )
                    # Remove original key
                    del encrypted_data[key]

        return encrypted_data

    def decrypt_dict(self, data: Dict[str, Any]) -> Dict:
        """
        Decrypt encrypted values in a dictionary

        Args:
            data: Dictionary with encrypted values

        Returns:
            Dictionary with encrypted values decrypted
        """
        decrypted_data = data.copy()

        # Find all encrypted keys (ending with __encrypted__)
        for key in list(decrypted_data.keys()):
            if key.endswith("__encrypted__"):
                # Get original key name
                original_key = key.replace("__encrypted__", "")
                encrypted_value = decrypted_data[key]

                try:
                    # Decrypt value
                    decrypted_value = self.decrypt(encrypted_value)
                    decrypted_data[original_key] = decrypted_value
                    # Remove encrypted key
                    del decrypted_data[key]
                except ValueError as e:
                    logger.error(
                        f"❌ Failed to decrypt {original_key}", error=str(e)
                    )
                    # Keep encrypted value if decryption fails
                    decrypted_data[original_key] = encrypted_value

        return decrypted_data


class SecretManager:
    """
    Manages encrypted storage of secrets and sensitive configuration

    Handles:
    - Database credentials
    - API keys and tokens
    - JWT secrets
    - Connection strings
    """

    def __init__(self, encryption_manager: EncryptionManager = None):
        """
        Initialize secret manager

        Args:
            encryption_manager: EncryptionManager instance.
                              If None, creates a new one.
        """
        self.encryption = encryption_manager or EncryptionManager()
        self.secrets = {}

    def store_secret(self, key: str, value: str):
        """
        Store an encrypted secret

        Args:
            key: Secret identifier
            value: Secret value to encrypt
        """
        encrypted_value = self.encryption.encrypt(value)
        self.secrets[key] = encrypted_value
        logger.info(f"✅ Secret stored: {key}")

    def retrieve_secret(self, key: str) -> str:
        """
        Retrieve and decrypt a secret

        Args:
            key: Secret identifier

        Returns:
            Decrypted secret value

        Raises:
            KeyError: If secret not found
        """
        if key not in self.secrets:
            logger.error(f"❌ Secret not found: {key}")
            raise KeyError(f"Secret '{key}' not found")

        encrypted_value = self.secrets[key]
        return self.encryption.decrypt(encrypted_value)

    def store_secrets_from_dict(self, secrets_dict: Dict[str, str]):
        """
        Store multiple encrypted secrets from dictionary

        Args:
            secrets_dict: Dictionary of {key: value} pairs to encrypt
        """
        for key, value in secrets_dict.items():
            self.store_secret(key, value)

    def to_encrypted_json(self) -> str:
        """
        Serialize encrypted secrets to JSON

        Returns:
            JSON string containing encrypted secrets
        """
        return json.dumps(self.secrets)

    def from_encrypted_json(self, json_str: str):
        """
        Load encrypted secrets from JSON

        Args:
            json_str: JSON string containing encrypted secrets
        """
        self.secrets = json.loads(json_str)
        logger.info(f"✅ Loaded {len(self.secrets)} encrypted secrets")


# Global encryption manager instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def get_secret_manager() -> SecretManager:
    """Get or create global secret manager instance"""
    return SecretManager(get_encryption_manager())


# Convenience functions for direct use
def encrypt_value(plaintext: str) -> str:
    """Encrypt a value using global encryption manager"""
    return get_encryption_manager().encrypt(plaintext)


def decrypt_value(encrypted_data: str) -> str:
    """Decrypt a value using global encryption manager"""
    return get_encryption_manager().decrypt(encrypted_data)
