"""
Phase 3 Task 20: Comprehensive Unit Tests for Key Rotation
Tests for EncryptionManager and SecretManager key rotation functionality

Test Coverage:
- Key version derivation
- Key rotation workflow
- Re-encryption functionality
- Version detection and extraction
- Migration tools
- Backward compatibility with legacy format
- Error handling and edge cases
"""

import pytest
import base64
import os
from datetime import datetime

from app.core.encryption import EncryptionManager, SecretManager


class TestEncryptionManagerKeyVersioning:
    """Test EncryptionManager key versioning capabilities"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager with default key version"""
        return EncryptionManager(master_password="test-password-12345", key_version=1)

    def test_initialization_with_default_version(self):
        """Test manager initializes with version 1 by default"""
        manager = EncryptionManager(master_password="test-password")
        assert manager.current_key_version == 1
        assert 1 in manager._cipher_keys
        assert 1 in manager._key_metadata

    def test_initialization_with_custom_version(self):
        """Test manager initializes with custom key version"""
        manager = EncryptionManager(master_password="test-password", key_version=5)
        assert manager.current_key_version == 5
        assert 5 in manager._cipher_keys
        assert 5 in manager._key_metadata

    def test_key_metadata_tracking(self, manager):
        """Test key metadata is tracked correctly"""
        metadata = manager._key_metadata[1]
        assert "created_at" in metadata
        assert "rotated_at" in metadata
        assert metadata["rotated_at"] is None  # Not rotated yet

        # Verify timestamp format
        created_at = metadata["created_at"]
        assert isinstance(created_at, str)
        datetime.fromisoformat(created_at)  # Should not raise

    def test_get_key_info(self, manager):
        """Test get_key_info returns correct information"""
        info = manager.get_key_info()

        assert info["current_version"] == 1
        assert 1 in info["available_versions"]
        assert 1 in info["key_metadata"]
        assert info["key_metadata"][1]["rotated_at"] is None


class TestKeyRotation:
    """Test key rotation functionality"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for rotation tests"""
        return EncryptionManager(master_password="rotation-test-pwd", key_version=1)

    def test_successful_key_rotation(self, manager):
        """Test successful rotation to new key version"""
        result = manager.rotate_key(new_version=2)

        assert result is True
        assert manager.current_key_version == 2
        assert 2 in manager._cipher_keys
        assert 2 in manager._key_metadata

        # Old key should still exist
        assert 1 in manager._cipher_keys

        # Old key should be marked as rotated
        assert manager._key_metadata[1]["rotated_at"] is not None

    def test_rotation_increments_version(self, manager):
        """Test multiple rotations increment version correctly"""
        manager.rotate_key(2)
        manager.rotate_key(3)
        manager.rotate_key(4)

        assert manager.current_key_version == 4
        assert all(v in manager._cipher_keys for v in [1, 2, 3, 4])

    def test_rotation_fails_with_same_version(self, manager):
        """Test rotation fails when new version <= current version"""
        result = manager.rotate_key(new_version=1)
        assert result is False
        assert manager.current_key_version == 1

    def test_rotation_fails_with_lower_version(self, manager):
        """Test rotation fails when new version < current version"""
        manager.rotate_key(3)
        result = manager.rotate_key(new_version=2)

        assert result is False
        assert manager.current_key_version == 3

    def test_rotation_timestamp_recorded(self, manager):
        """Test rotation timestamp is recorded for old key"""
        before_rotation = datetime.utcnow()
        manager.rotate_key(2)
        after_rotation = datetime.utcnow()

        rotated_at_str = manager._key_metadata[1]["rotated_at"]
        rotated_at = datetime.fromisoformat(rotated_at_str)

        assert before_rotation <= rotated_at <= after_rotation


class TestEncryptionWithVersioning:
    """Test encryption with key versioning"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for encryption tests"""
        return EncryptionManager(master_password="encrypt-test-pwd", key_version=1)

    def test_encrypt_includes_version_prefix(self, manager):
        """Test encrypted data includes version prefix"""
        plaintext = "sensitive data"
        encrypted = manager.encrypt(plaintext)

        # Decode to check format
        encrypted_bytes = base64.b64decode(encrypted)
        version_byte = encrypted_bytes[0]

        assert version_byte == 1  # Current version

    def test_encrypt_with_different_versions(self, manager):
        """Test encryption with different key versions"""
        # Encrypt with version 1
        encrypted_v1 = manager.encrypt("data v1")
        version_v1 = manager.get_encrypted_version(encrypted_v1)
        assert version_v1 == 1

        # Rotate and encrypt with version 2
        manager.rotate_key(2)
        encrypted_v2 = manager.encrypt("data v2")
        version_v2 = manager.get_encrypted_version(encrypted_v2)
        assert version_v2 == 2

    def test_encrypt_bytes_input(self, manager):
        """Test encryption with bytes input"""
        plaintext_bytes = b"binary data"
        encrypted = manager.encrypt(plaintext_bytes)

        decrypted = manager.decrypt(encrypted)
        assert decrypted == "binary data"

    def test_encrypt_unicode_content(self, manager):
        """Test encryption with unicode content"""
        plaintext = "测试数据 🔒"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)

        assert decrypted == plaintext


class TestDecryptionWithVersioning:
    """Test decryption with key versioning"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for decryption tests"""
        return EncryptionManager(master_password="decrypt-test-pwd", key_version=1)

    def test_decrypt_current_version(self, manager):
        """Test decrypting data encrypted with current version"""
        plaintext = "test data"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)

        assert decrypted == plaintext

    def test_decrypt_old_version_after_rotation(self, manager):
        """Test decrypting data encrypted with old version after rotation"""
        plaintext = "old version data"
        encrypted_v1 = manager.encrypt(plaintext)

        # Rotate key
        manager.rotate_key(2)

        # Should still decrypt v1 data
        decrypted = manager.decrypt(encrypted_v1)
        assert decrypted == plaintext

    def test_decrypt_multiple_old_versions(self, manager):
        """Test decrypting data from multiple old versions"""
        data_v1 = "version 1 data"
        encrypted_v1 = manager.encrypt(data_v1)

        manager.rotate_key(2)
        data_v2 = "version 2 data"
        encrypted_v2 = manager.encrypt(data_v2)

        manager.rotate_key(3)
        data_v3 = "version 3 data"
        encrypted_v3 = manager.encrypt(data_v3)

        # All should decrypt correctly
        assert manager.decrypt(encrypted_v1) == data_v1
        assert manager.decrypt(encrypted_v2) == data_v2
        assert manager.decrypt(encrypted_v3) == data_v3

    def test_decrypt_auto_derives_missing_version(self, manager):
        """Test decrypt auto-derives key for missing version"""
        # Encrypt with version 1
        encrypted = manager.encrypt("test")

        # Create new manager without version 1 key
        manager2 = EncryptionManager(master_password="decrypt-test-pwd", key_version=2)

        # Remove version 1 key
        if 1 in manager2._cipher_keys:
            del manager2._cipher_keys[1]

        # Should auto-derive version 1 key and decrypt successfully
        decrypted = manager2.decrypt(encrypted)
        assert decrypted == "test"
        assert 1 in manager2._cipher_keys  # Key was auto-derived


class TestBackwardCompatibility:
    """Test backward compatibility with legacy encryption format"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for compatibility tests"""
        return EncryptionManager(master_password="compat-test-pwd", key_version=1)

    def test_decrypt_legacy_format_without_version(self, manager):
        """Test decrypting legacy format (no version prefix)"""
        # Simulate legacy encryption (no version byte)
        plaintext = "legacy data"
        plaintext_bytes = plaintext.encode("utf-8")

        nonce = os.urandom(12)
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        cipher = AESGCM(manager._cipher_key)
        ciphertext = cipher.encrypt(nonce, plaintext_bytes, None)

        # Create legacy format: base64(nonce + ciphertext)
        legacy_encrypted = base64.b64encode(nonce + ciphertext).decode("utf-8")

        # Should decrypt successfully
        decrypted = manager.decrypt(legacy_encrypted)
        assert decrypted == plaintext

    def test_get_encrypted_version_returns_none_for_legacy(self, manager):
        """Test get_encrypted_version returns None for legacy format"""
        # Create legacy format encryption
        plaintext_bytes = b"legacy"
        nonce = os.urandom(12)
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        cipher = AESGCM(manager._cipher_key)
        ciphertext = cipher.encrypt(nonce, plaintext_bytes, None)
        legacy_encrypted = base64.b64encode(nonce + ciphertext).decode("utf-8")

        version = manager.get_encrypted_version(legacy_encrypted)
        assert version is None


class TestReEncryption:
    """Test re-encryption functionality"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for re-encryption tests"""
        return EncryptionManager(master_password="reencrypt-test-pwd", key_version=1)

    def test_re_encrypt_to_current_version(self, manager):
        """Test re-encrypting data to current version"""
        plaintext = "data to re-encrypt"
        encrypted_v1 = manager.encrypt(plaintext)

        # Re-encrypt to current version (should work)
        re_encrypted = manager.re_encrypt(encrypted_v1)

        # Should decrypt to same plaintext
        decrypted = manager.decrypt(re_encrypted)
        assert decrypted == plaintext

    def test_re_encrypt_to_target_version(self, manager):
        """Test re-encrypting data to specific target version"""
        plaintext = "data to re-encrypt"
        encrypted_v1 = manager.encrypt(plaintext)

        # Rotate to version 2
        manager.rotate_key(2)

        # Re-encrypt v1 data to v2
        re_encrypted = manager.re_encrypt(encrypted_v1, target_version=2)

        # Verify new version
        new_version = manager.get_encrypted_version(re_encrypted)
        assert new_version == 2

        # Verify decryption
        decrypted = manager.decrypt(re_encrypted)
        assert decrypted == plaintext

    def test_re_encrypt_preserves_content(self, manager):
        """Test re-encryption preserves original content"""
        plaintext = "important data 🔐"
        encrypted = manager.encrypt(plaintext)

        manager.rotate_key(2)
        re_encrypted = manager.re_encrypt(encrypted, target_version=2)

        decrypted = manager.decrypt(re_encrypted)
        assert decrypted == plaintext

    def test_re_encrypt_multiple_times(self, manager):
        """Test re-encrypting data multiple times"""
        plaintext = "multi-re-encrypt"
        encrypted = manager.encrypt(plaintext)

        # Re-encrypt through multiple versions
        for version in [2, 3, 4]:
            manager.rotate_key(version)
            encrypted = manager.re_encrypt(encrypted, target_version=version)

            # Verify each step
            assert manager.get_encrypted_version(encrypted) == version
            assert manager.decrypt(encrypted) == plaintext


class TestVersionDetection:
    """Test encryption version detection"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for version detection tests"""
        return EncryptionManager(master_password="version-test-pwd", key_version=1)

    def test_get_encrypted_version_for_v1(self, manager):
        """Test detecting version 1 encrypted data"""
        encrypted = manager.encrypt("test v1")
        version = manager.get_encrypted_version(encrypted)

        assert version == 1

    def test_get_encrypted_version_for_multiple_versions(self, manager):
        """Test detecting versions for multiple encrypted data"""
        encrypted_v1 = manager.encrypt("v1 data")

        manager.rotate_key(2)
        encrypted_v2 = manager.encrypt("v2 data")

        manager.rotate_key(3)
        encrypted_v3 = manager.encrypt("v3 data")

        assert manager.get_encrypted_version(encrypted_v1) == 1
        assert manager.get_encrypted_version(encrypted_v2) == 2
        assert manager.get_encrypted_version(encrypted_v3) == 3

    def test_get_encrypted_version_invalid_base64(self, manager):
        """Test version detection with invalid base64"""
        version = manager.get_encrypted_version("not-base64!!!")
        assert version is None

    def test_get_encrypted_version_too_short(self, manager):
        """Test version detection with data too short"""
        short_data = base64.b64encode(b"short").decode("utf-8")
        version = manager.get_encrypted_version(short_data)
        assert version is None


class TestSecretManagerMigration:
    """Test SecretManager migration tools"""

    @pytest.fixture
    def secret_manager(self):
        """Create SecretManager for migration tests"""
        encryption_mgr = EncryptionManager(master_password="migration-test-pwd", key_version=1)
        return SecretManager(encryption_manager=encryption_mgr)

    def test_migrate_to_key_version_success(self, secret_manager):
        """Test successful migration of all secrets"""
        # Add some secrets with version 1
        secret_manager.store_secret("db_password", "secret123")
        secret_manager.store_secret("api_key", "key456")
        secret_manager.store_secret("jwt_secret", "jwt789")

        # Rotate to version 2
        secret_manager.encryption.rotate_key(2)

        # Migrate all secrets to version 2
        report = secret_manager.migrate_to_key_version(2)

        assert report["target_version"] == 2
        assert report["total_secrets"] == 3
        assert report["migrated"] == 3
        assert report["failed"] == 0
        assert report["already_current"] == 0
        assert len(report["errors"]) == 0

    def test_migrate_already_current_version(self, secret_manager):
        """Test migration when secrets already at target version"""
        secret_manager.store_secret("test", "value")

        # Already at version 1, try to migrate to version 1
        report = secret_manager.migrate_to_key_version(1)

        assert report["already_current"] == 1
        assert report["migrated"] == 0

    def test_migrate_partial_success(self, secret_manager):
        """Test migration with some secrets at current version"""
        # Add secret with version 1
        secret_manager.store_secret("old_secret", "value1")

        # Rotate and add secret with version 2
        secret_manager.encryption.rotate_key(2)
        secret_manager.store_secret("new_secret", "value2")

        # Migrate to version 2 (one already current, one needs migration)
        report = secret_manager.migrate_to_key_version(2)

        assert report["already_current"] == 1  # new_secret
        assert report["migrated"] == 1  # old_secret

    def test_migrate_report_structure(self, secret_manager):
        """Test migration report contains all required fields"""
        secret_manager.store_secret("test", "value")
        report = secret_manager.migrate_to_key_version(1)

        assert "target_version" in report
        assert "total_secrets" in report
        assert "migrated" in report
        assert "failed" in report
        assert "already_current" in report
        assert "errors" in report
        assert "start_time" in report
        assert "end_time" in report

        # Verify timestamps are valid ISO format
        datetime.fromisoformat(report["start_time"])
        datetime.fromisoformat(report["end_time"])

    def test_migrate_preserves_secret_values(self, secret_manager):
        """Test migration preserves secret values after re-encryption"""
        secrets = {
            "password1": "secret123",
            "password2": "secret456",
            "api_key": "key789",
        }

        for key, value in secrets.items():
            secret_manager.store_secret(key, value)

        # Rotate and migrate
        secret_manager.encryption.rotate_key(2)
        secret_manager.migrate_to_key_version(2)

        # Verify all values preserved
        for key, expected_value in secrets.items():
            actual_value = secret_manager.retrieve_secret(key)
            assert actual_value == expected_value


class TestVersionReport:
    """Test version reporting functionality"""

    @pytest.fixture
    def secret_manager(self):
        """Create SecretManager for version report tests"""
        encryption_mgr = EncryptionManager(master_password="report-test-pwd", key_version=1)
        return SecretManager(encryption_manager=encryption_mgr)

    def test_version_report_single_version(self, secret_manager):
        """Test version report with all secrets at same version"""
        secret_manager.store_secret("s1", "v1")
        secret_manager.store_secret("s2", "v2")
        secret_manager.store_secret("s3", "v3")

        report = secret_manager.get_version_report()

        assert report["total_secrets"] == 3
        assert report["current_encryption_version"] == 1
        assert report["version_distribution"][1] == 3
        assert report["needs_migration"] == 0

    def test_version_report_multiple_versions(self, secret_manager):
        """Test version report with secrets at different versions"""
        # Add secrets with version 1
        secret_manager.store_secret("s1", "v1")
        secret_manager.store_secret("s2", "v2")

        # Rotate and add secrets with version 2
        secret_manager.encryption.rotate_key(2)
        secret_manager.store_secret("s3", "v3")
        secret_manager.store_secret("s4", "v4")

        report = secret_manager.get_version_report()

        assert report["total_secrets"] == 4
        assert report["current_encryption_version"] == 2
        assert report["version_distribution"][1] == 2
        assert report["version_distribution"][2] == 2
        assert report["needs_migration"] == 2  # The v1 secrets

    def test_version_report_after_migration(self, secret_manager):
        """Test version report shows correct status after migration"""
        # Setup mixed versions
        secret_manager.store_secret("s1", "v1")
        secret_manager.encryption.rotate_key(2)
        secret_manager.store_secret("s2", "v2")

        # Before migration
        report_before = secret_manager.get_version_report()
        assert report_before["needs_migration"] == 1

        # Migrate
        secret_manager.migrate_to_key_version(2)

        # After migration
        report_after = secret_manager.get_version_report()
        assert report_after["needs_migration"] == 0
        assert report_after["version_distribution"][2] == 2

    def test_version_report_empty_secrets(self):
        """Test version report with no secrets"""
        encryption_mgr = EncryptionManager(master_password="empty-test", key_version=1)
        manager = SecretManager(encryption_manager=encryption_mgr)
        report = manager.get_version_report()

        assert report["total_secrets"] == 0
        assert report["version_distribution"] == {}
        assert report["legacy_format_count"] == 0
        assert report["needs_migration"] == 0


class TestErrorHandling:
    """Test error handling in key rotation"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for error tests"""
        return EncryptionManager(master_password="error-test-pwd")

    def test_decrypt_invalid_base64(self, manager):
        """Test decryption handles invalid base64"""
        with pytest.raises(Exception):
            manager.decrypt("not-valid-base64!!!")

    def test_decrypt_corrupted_data(self, manager):
        """Test decryption handles corrupted encrypted data"""
        corrupted = base64.b64encode(b"corrupted data").decode("utf-8")

        with pytest.raises(Exception):
            manager.decrypt(corrupted)

    def test_rotate_key_validation(self, manager):
        """Test key rotation validates version number"""
        # Test with same version
        assert manager.rotate_key(1) is False

        # Test with lower version
        manager.rotate_key(5)
        assert manager.rotate_key(3) is False

    def test_add_old_key_version_duplicate(self, manager):
        """Test adding duplicate old key version"""
        # This should work without error
        manager.add_old_key_version(10)
        manager.add_old_key_version(10)  # Duplicate

        # Should have key for version 10
        assert 10 in manager._cipher_keys


class TestConcurrentAccess:
    """Test thread-safe operations"""

    @pytest.fixture
    def manager(self):
        """Create EncryptionManager for concurrency tests"""
        return EncryptionManager(master_password="concurrent-test")

    def test_concurrent_encryption(self, manager):
        """Test concurrent encryption operations"""
        import threading

        results = []
        errors = []

        def encrypt_data(data: str):
            try:
                encrypted = manager.encrypt(data)
                decrypted = manager.decrypt(encrypted)
                results.append(decrypted)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        test_data = [f"data-{i}" for i in range(10)]

        for data in test_data:
            t = threading.Thread(target=encrypt_data, args=(data,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify all operations succeeded
        assert len(errors) == 0
        assert len(results) == 10
        assert sorted(results) == sorted(test_data)


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""

    def test_full_key_rotation_workflow(self):
        """Test complete key rotation workflow"""
        # 1. Initialize with version 1
        encryption_mgr = EncryptionManager(master_password="workflow-test", key_version=1)
        manager = SecretManager(encryption_manager=encryption_mgr)

        # 2. Add secrets
        manager.store_secret("db_password", "password123")
        manager.store_secret("api_key", "key456")

        # 3. Get version report
        report_v1 = manager.get_version_report()
        assert report_v1["current_encryption_version"] == 1
        assert report_v1["needs_migration"] == 0

        # 4. Rotate key
        manager.encryption.rotate_key(2)

        # 5. Check version report (should show migration needed)
        report_v2 = manager.get_version_report()
        assert report_v2["current_encryption_version"] == 2
        assert report_v2["needs_migration"] == 2  # Both secrets need migration

        # 6. Migrate secrets
        migration_report = manager.migrate_to_key_version(2)
        assert migration_report["migrated"] == 2
        assert migration_report["failed"] == 0

        # 7. Verify migration complete
        final_report = manager.get_version_report()
        assert final_report["needs_migration"] == 0

        # 8. Verify secrets still accessible
        assert manager.retrieve_secret("db_password") == "password123"
        assert manager.retrieve_secret("api_key") == "key456"

    def test_gradual_migration_scenario(self):
        """Test gradual migration with mixed versions"""
        encryption_mgr = EncryptionManager(master_password="gradual-test", key_version=1)
        manager = SecretManager(encryption_manager=encryption_mgr)

        # Add secrets with v1
        manager.store_secret("old1", "value1")
        manager.store_secret("old2", "value2")

        # Rotate to v2
        manager.encryption.rotate_key(2)

        # Add new secrets with v2
        manager.store_secret("new1", "value3")
        manager.store_secret("new2", "value4")

        # System should handle mixed versions
        assert manager.retrieve_secret("old1") == "value1"  # v1 secret
        assert manager.retrieve_secret("new1") == "value3"  # v2 secret

        # Migrate old secrets
        manager.migrate_to_key_version(2)

        # All secrets should still work
        assert manager.retrieve_secret("old1") == "value1"
        assert manager.retrieve_secret("old2") == "value2"
        assert manager.retrieve_secret("new1") == "value3"
        assert manager.retrieve_secret("new2") == "value4"
