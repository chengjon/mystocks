"""
Security Tests: Data Encryption and Secure Configuration
Task 1.3: Sensitive Data Encryption

Tests for:
- AES-256-GCM encryption/decryption
- Secure configuration management
- Database credential encryption
- API key protection
- JWT secret protection
"""

import pytest
import os
import tempfile
from pathlib import Path

# Add paths for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))


# ============================================================================
# PART 1: Encryption Manager Tests
# ============================================================================


class TestEncryptionManager:
    """Test AES-256-GCM encryption and decryption"""

    @staticmethod
    def get_encryption_manager():
        """Get EncryptionManager with test password"""
        try:
            from app.core.encryption import EncryptionManager

            return EncryptionManager(master_password="test-master-password-123")
        except ImportError:
            pytest.skip("EncryptionManager not available")
            return None

    def test_encryption_decryption_roundtrip(self):
        """Encryption followed by decryption returns original data"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "database_password_secret_12345"
        encrypted = em.encrypt(plaintext)
        decrypted = em.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypted_data_is_base64_encoded(self):
        """Encrypted data is valid base64 string"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "test_data"
        encrypted = em.encrypt(plaintext)

        # Should be valid base64
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

        # Should decode successfully
        import base64

        try:
            base64.b64decode(encrypted)
        except Exception:
            pytest.fail("Encrypted data is not valid base64")

    def test_encryption_produces_different_output_each_time(self):
        """Same plaintext produces different ciphertext (due to random nonce)"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "same_password"
        encrypted1 = em.encrypt(plaintext)
        encrypted2 = em.encrypt(plaintext)

        # Due to random nonce, ciphertexts should be different
        assert encrypted1 != encrypted2

        # But both should decrypt to same value
        assert em.decrypt(encrypted1) == plaintext
        assert em.decrypt(encrypted2) == plaintext

    def test_decryption_fails_with_wrong_key(self):
        """Decryption with wrong master password fails"""
        em1 = self.get_encryption_manager()
        if not em1:
            pytest.skip("EncryptionManager not available")

        plaintext = "secret_data"
        encrypted = em1.encrypt(plaintext)

        # Create manager with different password
        from app.core.encryption import EncryptionManager

        em2 = EncryptionManager(master_password="different-password")

        # Decryption should fail
        with pytest.raises(ValueError):
            em2.decrypt(encrypted)

    def test_decryption_fails_with_tampered_data(self):
        """Decryption fails if ciphertext is tampered"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "important_data"
        encrypted = em.encrypt(plaintext)

        # Tamper with encrypted data
        tampered = encrypted[:-4] + "XXXX"

        # Decryption should fail
        with pytest.raises(ValueError):
            em.decrypt(tampered)

    def test_encrypt_bytes_input(self):
        """Encryption handles bytes input correctly"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext_bytes = b"binary_password"
        encrypted = em.encrypt(plaintext_bytes)
        decrypted = em.decrypt(encrypted)

        assert decrypted == plaintext_bytes.decode("utf-8")

    def test_encrypt_large_data(self):
        """Encryption handles large data correctly"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        # Create large data (1MB)
        plaintext = "x" * (1024 * 1024)
        encrypted = em.encrypt(plaintext)
        decrypted = em.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_special_characters(self):
        """Encryption handles special characters correctly"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "password!@#$%^&*()|<>?{}[]\\\"';:,./"
        encrypted = em.encrypt(plaintext)
        decrypted = em.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_unicode_data(self):
        """Encryption handles Unicode characters correctly"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "密码🔐中文日本語한글"
        encrypted = em.encrypt(plaintext)
        decrypted = em.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_dict_multiple_keys(self):
        """Encrypt specific keys in dictionary"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        data = {
            "host": "localhost",
            "port": 5432,
            "username": "admin",
            "password": "secret123",
            "api_key": "sk-123456",
        }

        encrypted_data = em.encrypt_dict(data, ["password", "api_key"])

        # Original keys should be removed
        assert "password" not in encrypted_data
        assert "api_key" not in encrypted_data

        # Encrypted keys should be present
        assert "password__encrypted__" in encrypted_data
        assert "api_key__encrypted__" in encrypted_data

        # Non-encrypted keys should remain
        assert encrypted_data["host"] == "localhost"
        assert encrypted_data["port"] == 5432

    def test_decrypt_dict_recovery(self):
        """Decrypt dictionary recovers original sensitive values"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        original = {
            "host": "localhost",
            "password": "secret123",
            "api_key": "sk-123456",
        }

        encrypted = em.encrypt_dict(original, ["password", "api_key"])
        decrypted = em.decrypt_dict(encrypted)

        # All original keys should be restored
        assert decrypted["host"] == "localhost"
        assert decrypted["password"] == "secret123"
        assert decrypted["api_key"] == "sk-123456"


# ============================================================================
# PART 2: Secure Config Tests
# ============================================================================


class TestSecureConfig:
    """Test secure configuration management"""

    @staticmethod
    def get_secure_config():
        """Get SecureConfig instance"""
        try:
            from app.core.secure_config import SecureConfig
            from app.core.encryption import EncryptionManager

            em = EncryptionManager(master_password="test-master-password-123")
            return SecureConfig(em)
        except ImportError:
            pytest.skip("SecureConfig not available")
            return None

    def test_store_and_retrieve_database_credentials(self):
        """Store and retrieve encrypted database credentials"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="secure_password_123",
            database="mystocks",
        )

        creds = config.get_database_credentials("postgresql")

        assert creds["host"] == "localhost"
        assert creds["port"] == 5432
        assert creds["user"] == "postgres"
        assert creds["password"] == "secure_password_123"
        assert creds["database"] == "mystocks"

    def test_build_postgresql_connection_string(self):
        """Build PostgreSQL connection string from encrypted credentials"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="postgresql",
            host="db.example.com",
            port=5432,
            user="pguser",
            password="pgpassword",
            database="testdb",
        )

        conn_str = config.build_connection_string("postgresql")

        assert "postgresql+psycopg2://" in conn_str
        assert "pguser:pgpassword" in conn_str
        assert "db.example.com:5432" in conn_str
        assert "testdb" in conn_str

    def test_build_mysql_connection_string(self):
        """Build MySQL connection string from encrypted credentials"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="mysql",
            host="mysql.example.com",
            port=3306,
            user="mysqluser",
            password="mysqlpass",
            database="mydb",
        )

        conn_str = config.build_connection_string("mysql")

        assert "mysql+pymysql://" in conn_str
        assert "mysqluser:mysqlpass" in conn_str
        assert "mysql.example.com:3306" in conn_str

    def test_build_tdengine_connection_string(self):
        """Build TDengine connection string from encrypted credentials"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="tdengine",
            host="td.example.com",
            port=6030,
            user="root",
            password="tdpass",
            database="market_data",
        )

        conn_str = config.build_connection_string("tdengine")

        assert "taos://" in conn_str
        assert "root:tdpass" in conn_str
        assert "td.example.com:6030" in conn_str

    def test_store_and_retrieve_api_key(self):
        """Store and retrieve encrypted API key"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        api_key = "sk-proj-abcdef123456"
        config.set_api_key("openai", api_key)

        retrieved_key = config.get_api_key("openai")
        assert retrieved_key == api_key

    def test_store_and_retrieve_jwt_secret(self):
        """Store and retrieve encrypted JWT secret"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        jwt_secret = "super-secret-jwt-key-change-in-production"
        config.set_jwt_secret(jwt_secret)

        retrieved_secret = config.get_jwt_secret()
        assert retrieved_secret == jwt_secret

    def test_save_and_load_encrypted_config_file(self):
        """Save and load configuration from encrypted file"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="secret_pass",
            database="mydb",
        )
        config.set_api_key("service1", "api_key_value")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # Save
            assert config.save_to_file(temp_path) is True

            # Load into new config instance
            from app.core.secure_config import SecureConfig
            from app.core.encryption import EncryptionManager

            em = EncryptionManager(master_password="test-master-password-123")
            new_config = SecureConfig(em)
            assert new_config.load_from_file(temp_path) is True

            # Verify data
            creds = new_config.get_database_credentials("postgresql")
            assert creds["password"] == "secret_pass"
            assert new_config.get_api_key("service1") == "api_key_value"

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_missing_database_credentials_raises_error(self):
        """Retrieving non-existent database credentials raises KeyError"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        with pytest.raises(KeyError):
            config.get_database_credentials("nonexistent")

    def test_get_missing_api_key_raises_error(self):
        """Retrieving non-existent API key raises KeyError"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        with pytest.raises(KeyError):
            config.get_api_key("nonexistent")

    def test_verify_configuration_integrity(self):
        """Verify that all encrypted configuration can be decrypted"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="user",
            password="pass",
        )
        config.set_api_key("service", "key")
        config.set_jwt_secret("secret")

        results = config.verify_configuration()

        # All encrypted values should verify successfully
        assert all(results.values())

    def test_to_dict_with_decryption(self):
        """Export configuration with decrypted values"""
        config = self.get_secure_config()
        if not config:
            pytest.skip("SecureConfig not available")

        config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="secret",
        )

        config_dict = config.to_dict(include_encrypted=False)

        assert "db_postgresql" in config_dict
        assert config_dict["db_postgresql"]["password"] == "secret"


# ============================================================================
# PART 3: Security Best Practices Tests
# ============================================================================


class TestEncryptionSecurityPractices:
    """Test encryption security best practices"""

    @staticmethod
    def get_encryption_manager():
        try:
            from app.core.encryption import EncryptionManager

            return EncryptionManager(master_password="test-master-password-123")
        except ImportError:
            return None

    def test_encryption_uses_aes_256_gcm(self):
        """Encryption uses AES-256-GCM algorithm"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        # AES-256 uses 32-byte (256-bit) keys
        assert len(em._cipher_key) == 32

    def test_encryption_produces_authenticated_ciphertext(self):
        """GCM mode produces authenticated ciphertext"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "test_data"
        encrypted = em.encrypt(plaintext)

        # Tamper with the encrypted data
        import base64

        encrypted_bytes = base64.b64decode(encrypted)
        tampered_bytes = encrypted_bytes[:-1] + bytes([encrypted_bytes[-1] ^ 0xFF])
        tampered_encrypted = base64.b64encode(tampered_bytes).decode("utf-8")

        # Tampered data should fail authentication
        with pytest.raises(ValueError):
            em.decrypt(tampered_encrypted)

    def test_nonce_is_random(self):
        """Encryption uses random nonces for each encryption"""
        em = self.get_encryption_manager()
        if not em:
            pytest.skip("EncryptionManager not available")

        plaintext = "data"
        encrypted_list = [em.encrypt(plaintext) for _ in range(10)]

        # All ciphertexts should be different (random nonce)
        assert len(set(encrypted_list)) == len(encrypted_list)

    def test_file_permissions_restrictive(self):
        """Saved encrypted config file has restrictive permissions"""
        try:
            from app.core.secure_config import SecureConfig
            from app.core.encryption import EncryptionManager
        except ImportError:
            pytest.skip("SecureConfig not available")

        em = EncryptionManager(master_password="test-password")
        config = SecureConfig(em)
        config.set_api_key("test", "key")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            config.save_to_file(temp_path)

            # Check file permissions
            stat_info = os.stat(temp_path)
            mode = stat_info.st_mode & 0o777

            # Should be 0o600 (owner read/write only)
            assert mode == 0o600

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
