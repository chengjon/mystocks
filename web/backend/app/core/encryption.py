"""
Encryption utilities for protecting sensitive data
Task 1.3: Sensitive Data Encryption
Task 20: Key Rotation Support (Phase 3)

Provides AES-256-GCM encryption for:
- Database passwords and connection strings
- API keys and tokens
- User credentials
- Configuration secrets

Phase 3 Enhancements:
- Key versioning and rotation support
- Multiple encryption keys management
- Automatic migration from old to new keys
"""

import os
import base64
import json
from typing import Union, Dict, Any, Optional
from datetime import datetime
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

    Phase 3: Supports key versioning and rotation
    - Encrypted data format: base64(version:1byte + nonce:12bytes + ciphertext + tag)
    - Multiple key versions supported
    - Automatic decryption with appropriate key version
    """

    def __init__(self, master_password: str = None, key_version: int = 1):
        """
        Initialize encryption manager with master password

        Args:
            master_password: Master password for deriving encryption keys.
                           If not provided, uses ENCRYPTION_MASTER_PASSWORD env var
            key_version: Current key version (default: 1, for new encryptions)

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
        self.current_key_version = key_version

        # Phase 3: Support multiple key versions for rotation
        self._cipher_keys = {}  # {version: key_bytes}
        self._key_metadata = {}  # {version: {"created_at": datetime, "rotated_at": datetime}}

        self._setup_key()

    def _setup_key(self):
        """
        Derive encryption key from master password using PBKDF2

        Phase 3: Creates current key version and maintains backward compatibility
        """
        # Derive key for current version
        self._derive_key_for_version(self.current_key_version)

        # Maintain backward compatibility: _cipher_key points to current version
        self._cipher_key = self._cipher_keys[self.current_key_version]

        logger.info(
            "✅ Encryption key derived from master password",
            key_version=self.current_key_version,
        )

    def _derive_key_for_version(self, version: int):
        """
        Derive encryption key for a specific version

        Args:
            version: Key version number (1, 2, 3, ...)

        Phase 3: Each version uses a different salt for key derivation
        """
        # Version-specific salt for key derivation
        # SECURITY: Each version has a unique salt to ensure different keys
        salt = f"mystocks-encryption-salt-v{version}".encode()

        # Derive 32-byte key (256 bits) for AES-256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = kdf.derive(self.master_password.encode())
        self._cipher_keys[version] = key
        self._key_metadata[version] = {
            "created_at": datetime.utcnow().isoformat(),
            "rotated_at": None,
        }

        logger.debug(f"✅ Key derived for version {version}")

    def add_old_key_version(self, version: int):
        """
        Add an old key version for decryption of legacy data

        Args:
            version: Old key version to add

        Usage: During key rotation, add old versions to decrypt legacy data
        Phase 3: Enables gradual migration from old to new keys
        """
        if version not in self._cipher_keys:
            self._derive_key_for_version(version)
            logger.info(f"✅ Old key version {version} added for decryption")

    def rotate_key(self, new_version: int) -> bool:
        """
        Rotate to a new encryption key version

        Args:
            new_version: New key version number (must be > current_key_version)

        Returns:
            True if rotation successful

        Phase 3: Rotates to new key while maintaining old keys for decryption
        """
        if new_version <= self.current_key_version:
            logger.error(
                "❌ New key version must be greater than current version",
                current=self.current_key_version,
                new=new_version,
            )
            return False

        # Mark current key as rotated
        self._key_metadata[self.current_key_version]["rotated_at"] = datetime.utcnow().isoformat()

        # Derive new key
        self._derive_key_for_version(new_version)

        # Update current version
        old_version = self.current_key_version
        self.current_key_version = new_version
        self._cipher_key = self._cipher_keys[new_version]

        logger.info(
            "✅ Key rotation complete",
            old_version=old_version,
            new_version=new_version,
        )
        return True

    def get_key_info(self) -> Dict[str, Any]:
        """
        Get information about current and available key versions

        Returns:
            Dictionary with key version information

        Phase 3: Provides visibility into key rotation status
        """
        return {
            "current_version": self.current_key_version,
            "available_versions": list(self._cipher_keys.keys()),
            "key_metadata": self._key_metadata.copy(),
        }

    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """
        Encrypt plaintext using AES-256-GCM

        Args:
            plaintext: Data to encrypt (str or bytes)

        Returns:
            Base64-encoded encrypted data with version, IV, and tag

        Phase 3 Format: base64(version:1byte + nonce:12bytes + ciphertext + tag)
        - version: Key version used for encryption (1 byte, 0-255)
        - nonce: Random 12-byte nonce for GCM
        - ciphertext: Encrypted data with authentication tag
        """
        # Convert to bytes if string
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")

        # Generate random nonce (96 bits / 12 bytes for GCM)
        nonce = os.urandom(12)

        # Create cipher with current key version and encrypt
        cipher = AESGCM(self._cipher_key)
        ciphertext = cipher.encrypt(nonce, plaintext, None)

        # Phase 3: Prepend version byte
        version_byte = self.current_key_version.to_bytes(1, "big")

        # Combine version + nonce + ciphertext (which includes auth tag)
        encrypted_data = version_byte + nonce + ciphertext

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

        Phase 3: Supports both old format (no version) and new format (with version)
        - New format: base64(version:1byte + nonce:12bytes + ciphertext + tag)
        - Old format: base64(nonce:12bytes + ciphertext + tag)
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)

            # Phase 3: Check if data has version byte (length > 12 bytes for nonce alone)
            # New format: version (1 byte) + nonce (12 bytes) + ciphertext (variable)
            # Old format: nonce (12 bytes) + ciphertext (variable)

            if len(encrypted_bytes) > 13:  # Has at least version + nonce + 1 byte data
                # Try new format first
                version = int.from_bytes(encrypted_bytes[:1], "big")

                if version > 0 and version <= 255:
                    # Valid version byte detected
                    nonce = encrypted_bytes[1:13]  # Next 12 bytes
                    ciphertext = encrypted_bytes[13:]  # Remainder

                    # Get key for this version
                    if version not in self._cipher_keys:
                        # Try to derive missing key version
                        self.add_old_key_version(version)

                    if version in self._cipher_keys:
                        cipher = AESGCM(self._cipher_keys[version])
                        try:
                            plaintext = cipher.decrypt(nonce, ciphertext, None)
                            logger.debug(f"✅ Decrypted with key version {version}")
                            return plaintext.decode("utf-8")
                        except Exception:
                            pass  # Fall through to try old format

            # Fall back to old format (backward compatibility)
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]

            # Decrypt with current key (backward compatibility)
            cipher = AESGCM(self._cipher_key)
            plaintext = cipher.decrypt(nonce, ciphertext, None)

            logger.debug("✅ Decrypted with legacy format (no version)")
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
                    encrypted_data[f"{key}__encrypted__"] = self.encrypt(str(value))
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
                    logger.error(f"❌ Failed to decrypt {original_key}", error=str(e))
                    # Keep encrypted value if decryption fails
                    decrypted_data[original_key] = encrypted_value

        return decrypted_data

    def re_encrypt(self, encrypted_data: str, target_version: Optional[int] = None) -> str:
        """
        Re-encrypt data with a different key version

        Args:
            encrypted_data: Currently encrypted data
            target_version: Target key version (None = current version)

        Returns:
            Re-encrypted data with target key version

        Phase 3: Essential for key rotation migration
        Usage: During key rotation, re-encrypt all secrets with new key
        """
        # Decrypt with old key
        plaintext = self.decrypt(encrypted_data)

        # Temporarily switch to target version if specified
        if target_version is not None:
            original_version = self.current_key_version
            self.current_key_version = target_version

            # Ensure target key exists
            if target_version not in self._cipher_keys:
                self._derive_key_for_version(target_version)

            self._cipher_key = self._cipher_keys[target_version]

        # Encrypt with new key
        new_encrypted = self.encrypt(plaintext)

        # Restore original version if changed
        if target_version is not None:
            self.current_key_version = original_version
            self._cipher_key = self._cipher_keys[original_version]

        logger.debug(f"✅ Re-encrypted data with version {target_version or self.current_key_version}")
        return new_encrypted

    def get_encrypted_version(self, encrypted_data: str) -> Optional[int]:
        """
        Extract key version from encrypted data

        Args:
            encrypted_data: Encrypted data string

        Returns:
            Key version number, or None if legacy format (no version)

        Phase 3: Helps identify which secrets need re-encryption

        Note: Only versions 1-20 are considered valid to avoid misidentifying
        legacy format data (where first byte is random nonce data).
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)

            if len(encrypted_bytes) > 13:
                version = int.from_bytes(encrypted_bytes[:1], "big")
                # Only consider versions 1-20 as valid to reduce false positives
                # from legacy format (where first byte is random nonce data)
                if 1 <= version <= 20:
                    return version

            return None  # Legacy format or invalid version

        except Exception:
            return None


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

    def migrate_to_key_version(self, target_version: int) -> Dict[str, Any]:
        """
        Migrate all secrets to a new key version

        Args:
            target_version: Target key version for migration

        Returns:
            Migration report with success/failure statistics

        Phase 3 (Task 20): Essential for key rotation
        Usage: After rotating key, migrate all existing secrets
        """
        logger.info(
            f"🔄 Starting migration to key version {target_version}",
            total_secrets=len(self.secrets),
        )

        migration_report = {
            "target_version": target_version,
            "total_secrets": len(self.secrets),
            "migrated": 0,
            "failed": 0,
            "already_current": 0,
            "errors": [],
            "start_time": datetime.utcnow().isoformat(),
        }

        for key, encrypted_value in list(self.secrets.items()):
            try:
                # Check current version
                current_version = self.encryption.get_encrypted_version(encrypted_value)

                if current_version == target_version:
                    migration_report["already_current"] += 1
                    continue

                # Re-encrypt with target version
                new_encrypted = self.encryption.re_encrypt(encrypted_value, target_version)
                self.secrets[key] = new_encrypted
                migration_report["migrated"] += 1

                logger.debug(f"✅ Migrated secret: {key}")

            except Exception as e:
                migration_report["failed"] += 1
                migration_report["errors"].append({"key": key, "error": str(e)})
                logger.error(f"❌ Failed to migrate {key}", error=str(e))

        migration_report["end_time"] = datetime.utcnow().isoformat()

        logger.info(
            "✅ Migration complete",
            migrated=migration_report["migrated"],
            failed=migration_report["failed"],
            already_current=migration_report["already_current"],
        )

        return migration_report

    def get_version_report(self) -> Dict[str, Any]:
        """
        Generate report on key versions used by stored secrets

        Returns:
            Report with version distribution

        Phase 3 (Task 20): Helps identify secrets needing migration
        """
        version_counts = {}
        legacy_count = 0

        for key, encrypted_value in self.secrets.items():
            version = self.encryption.get_encrypted_version(encrypted_value)

            if version is None:
                legacy_count += 1
            else:
                version_counts[version] = version_counts.get(version, 0) + 1

        report = {
            "total_secrets": len(self.secrets),
            "version_distribution": version_counts,
            "legacy_format_count": legacy_count,
            "current_encryption_version": self.encryption.current_key_version,
            "needs_migration": sum(
                count for version, count in version_counts.items() if version != self.encryption.current_key_version
            )
            + legacy_count,
        }

        logger.info(
            "📊 Version report generated",
            total=report["total_secrets"],
            needs_migration=report["needs_migration"],
        )

        return report


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
