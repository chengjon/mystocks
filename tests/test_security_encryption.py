"""
Security tests for encryption and secure configuration helpers.

These tests validate the current backend contracts instead of skipping when the
backend package path is assembled incorrectly.
"""

import base64
import os
import stat
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "web" / "backend"

# Keep the repo root ahead of the backend path so the top-level `tests` package
# resolves to `/opt/claude/mystocks_spec/tests` instead of `web/backend/tests`.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(1, str(BACKEND_ROOT))

from app.core.encryption import EncryptionManager
from app.core.secure_config import SecureConfig


@pytest.fixture
def encryption_manager() -> EncryptionManager:
    return EncryptionManager(master_password="test-master-password-123")


@pytest.fixture
def secure_config(encryption_manager: EncryptionManager) -> SecureConfig:
    return SecureConfig(encryption_manager)


class TestEncryptionManager:
    def test_backend_security_modules_import_cleanly(self) -> None:
        assert EncryptionManager.__module__ == "app.core.encryption"
        assert SecureConfig.__module__ == "app.core.secure_config"

    def test_encryption_decryption_roundtrip(self, encryption_manager: EncryptionManager) -> None:
        plaintext = "database_password_secret_12345"
        encrypted = encryption_manager.encrypt(plaintext)

        assert encryption_manager.decrypt(encrypted) == plaintext

    def test_encrypted_data_is_base64_encoded(self, encryption_manager: EncryptionManager) -> None:
        encrypted = encryption_manager.encrypt("test_data")

        assert isinstance(encrypted, str)
        assert base64.b64decode(encrypted)

    def test_encryption_produces_different_output_each_time(self, encryption_manager: EncryptionManager) -> None:
        encrypted_one = encryption_manager.encrypt("same_password")
        encrypted_two = encryption_manager.encrypt("same_password")

        assert encrypted_one != encrypted_two
        assert encryption_manager.decrypt(encrypted_one) == "same_password"
        assert encryption_manager.decrypt(encrypted_two) == "same_password"

    def test_decryption_fails_with_wrong_key(self, encryption_manager: EncryptionManager) -> None:
        encrypted = encryption_manager.encrypt("secret_data")
        wrong_manager = EncryptionManager(master_password="different-password")

        with pytest.raises(ValueError):
            wrong_manager.decrypt(encrypted)

    def test_decryption_fails_with_tampered_data(self, encryption_manager: EncryptionManager) -> None:
        encrypted = encryption_manager.encrypt("important_data")
        tampered = encrypted[:-4] + "XXXX"

        with pytest.raises(ValueError):
            encryption_manager.decrypt(tampered)

    def test_encrypt_handles_bytes_input(self, encryption_manager: EncryptionManager) -> None:
        encrypted = encryption_manager.encrypt(b"binary_password")

        assert encryption_manager.decrypt(encrypted) == "binary_password"

    def test_encrypt_handles_large_unicode_payload(self, encryption_manager: EncryptionManager) -> None:
        plaintext = ("密码🔐中文日本語한글" * 64) + ("x" * 4096)
        encrypted = encryption_manager.encrypt(plaintext)

        assert encryption_manager.decrypt(encrypted) == plaintext

    def test_encrypt_dict_multiple_keys(self, encryption_manager: EncryptionManager) -> None:
        data = {
            "host": "localhost",
            "port": 5432,
            "username": "admin",
            "password": "secret123",
            "api_key": "sk-123456",
        }

        encrypted_data = encryption_manager.encrypt_dict(data, ["password", "api_key"])

        assert "password" not in encrypted_data
        assert "api_key" not in encrypted_data
        assert "password__encrypted__" in encrypted_data
        assert "api_key__encrypted__" in encrypted_data
        assert encrypted_data["host"] == "localhost"
        assert encrypted_data["port"] == 5432

    def test_decrypt_dict_recovery(self, encryption_manager: EncryptionManager) -> None:
        original = {
            "host": "localhost",
            "password": "secret123",
            "api_key": "sk-123456",
        }

        encrypted = encryption_manager.encrypt_dict(original, ["password", "api_key"])
        decrypted = encryption_manager.decrypt_dict(encrypted)

        assert decrypted["host"] == "localhost"
        assert decrypted["password"] == "secret123"
        assert decrypted["api_key"] == "sk-123456"

    def test_encryption_uses_256_bit_key(self, encryption_manager: EncryptionManager) -> None:
        assert len(encryption_manager._cipher_key) == 32

    def test_encryption_produces_authenticated_ciphertext(self, encryption_manager: EncryptionManager) -> None:
        encrypted = encryption_manager.encrypt("test_data")
        encrypted_bytes = base64.b64decode(encrypted)
        tampered_bytes = encrypted_bytes[:-1] + bytes([encrypted_bytes[-1] ^ 0xFF])
        tampered_encrypted = base64.b64encode(tampered_bytes).decode("utf-8")

        with pytest.raises(ValueError):
            encryption_manager.decrypt(tampered_encrypted)

    def test_nonce_is_random(self, encryption_manager: EncryptionManager) -> None:
        encrypted_values = [encryption_manager.encrypt("data") for _ in range(10)]

        assert len(set(encrypted_values)) == len(encrypted_values)


class TestSecureConfig:
    def test_store_and_retrieve_database_credentials(self, secure_config: SecureConfig) -> None:
        secure_config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="secure_password_123",
            database="mystocks",
        )

        creds = secure_config.get_database_credentials("postgresql")

        assert creds == {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "secure_password_123",
            "database": "mystocks",
        }

    def test_build_postgresql_connection_string(self, secure_config: SecureConfig) -> None:
        secure_config.set_database_credentials(
            db_type="postgresql",
            host="db.example.com",
            port=5432,
            user="pguser",
            password="pgpassword",
            database="testdb",
        )

        conn_str = secure_config.build_connection_string("postgresql")

        assert conn_str == "postgresql+psycopg2://pguser:pgpassword@db.example.com:5432/testdb"

    def test_build_tdengine_connection_string(self, secure_config: SecureConfig) -> None:
        secure_config.set_database_credentials(
            db_type="tdengine",
            host="td.example.com",
            port=6030,
            user="root",
            password="tdpass",
            database="market_data",
        )

        conn_str = secure_config.build_connection_string("tdengine")

        assert conn_str == "taos://root:tdpass@td.example.com:6030/market_data"

    def test_store_and_retrieve_api_key(self, secure_config: SecureConfig) -> None:
        secure_config.set_api_key("openai", "sk-proj-abcdef123456")

        assert secure_config.get_api_key("openai") == "sk-proj-abcdef123456"

    def test_store_and_retrieve_jwt_secret(self, secure_config: SecureConfig) -> None:
        secure_config.set_jwt_secret("super-secret-jwt-key-change-in-production")

        assert secure_config.get_jwt_secret() == "super-secret-jwt-key-change-in-production"

    def test_save_and_load_encrypted_config_file(self, secure_config: SecureConfig, tmp_path: Path) -> None:
        secure_config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="secret_pass",
            database="mydb",
        )
        secure_config.set_api_key("service1", "api_key_value")
        secure_config.set_jwt_secret("jwt-secret")

        config_path = tmp_path / "encrypted-config.json"

        assert secure_config.save_to_file(str(config_path)) is True

        loaded_config = SecureConfig(EncryptionManager(master_password="test-master-password-123"))
        assert loaded_config.load_from_file(str(config_path)) is True
        assert loaded_config.get_database_credentials("postgresql")["password"] == "secret_pass"
        assert loaded_config.get_api_key("service1") == "api_key_value"
        assert loaded_config.get_jwt_secret() == "jwt-secret"

    def test_get_missing_database_credentials_raises_error(self, secure_config: SecureConfig) -> None:
        with pytest.raises(KeyError):
            secure_config.get_database_credentials("nonexistent")

    def test_get_missing_api_key_raises_error(self, secure_config: SecureConfig) -> None:
        with pytest.raises(KeyError):
            secure_config.get_api_key("nonexistent")

    def test_verify_configuration_reports_current_top_level_encrypted_entries(self, secure_config: SecureConfig) -> None:
        secure_config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="user",
            password="pass",
        )
        secure_config.set_api_key("service", "key")
        secure_config.set_jwt_secret("secret")

        assert secure_config.verify_configuration() == {"jwt_secret_encrypted": True}

    def test_to_dict_decrypts_supported_top_level_fields(self, secure_config: SecureConfig) -> None:
        secure_config.set_database_credentials(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="secret",
        )
        secure_config.set_jwt_secret("jwt-secret")

        config_dict = secure_config.to_dict(include_encrypted=False)

        assert config_dict["jwt_secret"] == "jwt-secret"
        assert config_dict["db_postgresql"]["user"] == "postgres"
        assert "password_encrypted" in config_dict["db_postgresql"]

    def test_file_permissions_restrictive(self, secure_config: SecureConfig, tmp_path: Path) -> None:
        secure_config.set_api_key("test", "key")
        config_path = tmp_path / "permissions.json"

        assert secure_config.save_to_file(str(config_path)) is True

        mode = stat.S_IMODE(os.stat(config_path).st_mode)
        assert mode == 0o600


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
