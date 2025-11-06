"""
Secure configuration management for sensitive data
Task 1.3: Sensitive Data Encryption

Manages encrypted storage and retrieval of:
- Database credentials
- API keys
- Connection strings
- Authentication secrets
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
import structlog

from .encryption import EncryptionManager, SecretManager

logger = structlog.get_logger()


class SecureConfig:
    """
    Manages secure storage and retrieval of sensitive configuration

    SECURITY: All database passwords and API keys are encrypted at rest.
    Encryption key derived from ENCRYPTION_MASTER_PASSWORD environment variable.
    """

    def __init__(self, encryption_manager: EncryptionManager = None):
        """
        Initialize secure configuration manager

        Args:
            encryption_manager: Custom EncryptionManager or None for default
        """
        self.encryption = encryption_manager or EncryptionManager()
        self.secret_manager = SecretManager(self.encryption)
        self._encrypted_config_file = None
        self._config = {}

    def set_database_credentials(
        self,
        db_type: str,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str = None,
    ):
        """
        Store encrypted database credentials

        Args:
            db_type: Type of database (postgresql, tdengine, mysql)
            host: Database host
            port: Database port
            user: Database user
            password: Database password (will be encrypted)
            database: Database name (optional)

        SECURITY: Password is encrypted immediately
        """
        db_config = {
            "type": db_type,
            "host": host,
            "port": port,
            "user": user,
            "password_encrypted": self.encryption.encrypt(password),
        }

        if database:
            db_config["database"] = database

        self._config[f"db_{db_type}"] = db_config
        logger.info(f"✅ Database credentials stored for {db_type}")

    def get_database_credentials(self, db_type: str) -> Dict[str, Any]:
        """
        Retrieve decrypted database credentials

        Args:
            db_type: Type of database to retrieve

        Returns:
            Dictionary with decrypted credentials

        Raises:
            KeyError: If database credentials not found
        """
        key = f"db_{db_type}"

        if key not in self._config:
            raise KeyError(f"No credentials found for database: {db_type}")

        db_config = self._config[key].copy()

        # Decrypt password
        if "password_encrypted" in db_config:
            try:
                db_config["password"] = self.encryption.decrypt(
                    db_config["password_encrypted"]
                )
                del db_config["password_encrypted"]
            except ValueError as e:
                logger.error(
                    f"❌ Failed to decrypt {db_type} password", error=str(e)
                )
                raise

        return db_config

    def build_connection_string(
        self,
        db_type: str,
        driver: str = None,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> str:
        """
        Build database connection string from encrypted credentials

        Args:
            db_type: Type of database
            driver: Database driver (e.g., psycopg2, pymysql)
            pool_size: Connection pool size
            max_overflow: Max overflow connections

        Returns:
            Database connection string with decrypted credentials

        Raises:
            KeyError: If credentials not found
        """
        creds = self.get_database_credentials(db_type)

        host = creds["host"]
        port = creds["port"]
        user = creds["user"]
        password = creds["password"]
        database = creds.get("database", "")

        # Build appropriate connection string based on database type
        if db_type == "postgresql":
            driver = driver or "postgresql+psycopg2"
            conn_str = (
                f"{driver}://{user}:{password}@{host}:{port}/{database}"
            )

        elif db_type == "mysql":
            driver = driver or "mysql+pymysql"
            conn_str = (
                f"{driver}://{user}:{password}@{host}:{port}/{database}"
            )

        elif db_type == "tdengine":
            # TDengine uses custom connection format
            conn_str = f"taos://{user}:{password}@{host}:{port}/{database}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        logger.info(f"✅ Connection string built for {db_type}")
        return conn_str

    def set_api_key(self, service: str, api_key: str):
        """
        Store encrypted API key

        Args:
            service: Service name (e.g., 'akshare', 'tradingview')
            api_key: API key value (will be encrypted)

        SECURITY: API key is encrypted immediately
        """
        encrypted_key = self.encryption.encrypt(api_key)
        self._config[f"api_key_{service}"] = encrypted_key
        logger.info(f"✅ API key stored for {service}")

    def get_api_key(self, service: str) -> str:
        """
        Retrieve decrypted API key

        Args:
            service: Service name

        Returns:
            Decrypted API key

        Raises:
            KeyError: If API key not found
        """
        key = f"api_key_{service}"

        if key not in self._config:
            raise KeyError(f"No API key found for service: {service}")

        try:
            return self.encryption.decrypt(self._config[key])
        except ValueError as e:
            logger.error(f"❌ Failed to decrypt API key for {service}", error=str(e))
            raise

    def set_jwt_secret(self, secret: str):
        """
        Store encrypted JWT secret key

        Args:
            secret: JWT secret (will be encrypted)

        SECURITY: JWT secret is encrypted immediately
        """
        encrypted_secret = self.encryption.encrypt(secret)
        self._config["jwt_secret_encrypted"] = encrypted_secret
        logger.info("✅ JWT secret stored")

    def get_jwt_secret(self) -> str:
        """
        Retrieve decrypted JWT secret

        Returns:
            Decrypted JWT secret

        Raises:
            KeyError: If JWT secret not found
        """
        if "jwt_secret_encrypted" not in self._config:
            raise KeyError("JWT secret not configured")

        try:
            return self.encryption.decrypt(self._config["jwt_secret_encrypted"])
        except ValueError as e:
            logger.error("❌ Failed to decrypt JWT secret", error=str(e))
            raise

    def save_to_file(self, filepath: str) -> bool:
        """
        Save encrypted configuration to JSON file

        Args:
            filepath: Path to save encrypted config

        Returns:
            True if successful, False otherwise

        SECURITY: Configuration file contains only encrypted data
        """
        try:
            with open(filepath, "w") as f:
                json.dump(self._config, f, indent=2)

            # Restrict file permissions to owner only
            os.chmod(filepath, 0o600)
            logger.info(f"✅ Encrypted configuration saved to {filepath}")
            self._encrypted_config_file = filepath
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save encrypted config", error=str(e))
            return False

    def load_from_file(self, filepath: str) -> bool:
        """
        Load encrypted configuration from JSON file

        Args:
            filepath: Path to load encrypted config from

        Returns:
            True if successful, False otherwise

        SECURITY: Configuration is encrypted in file, decrypted only on retrieval
        """
        try:
            with open(filepath, "r") as f:
                self._config = json.load(f)

            self._encrypted_config_file = filepath
            logger.info(f"✅ Encrypted configuration loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load encrypted config", error=str(e))
            return False

    def to_dict(self, include_encrypted: bool = False) -> Dict[str, Any]:
        """
        Get configuration as dictionary

        Args:
            include_encrypted: If False, decrypt sensitive values before returning

        Returns:
            Configuration dictionary

        SECURITY: By default, returns decrypted values. Use include_encrypted=True
        only for storage/transmission scenarios.
        """
        config = {}

        for key, value in self._config.items():
            if include_encrypted:
                config[key] = value
            elif key.endswith("_encrypted"):
                # Decrypt encrypted values
                try:
                    original_key = key.replace("_encrypted", "")
                    config[original_key] = self.encryption.decrypt(value)
                except ValueError:
                    config[key] = value
            else:
                config[key] = value

        return config

    def verify_configuration(self) -> Dict[str, bool]:
        """
        Verify that all required encrypted data can be decrypted

        Returns:
            Dictionary of {key: is_valid} for each encrypted value
        """
        verification_results = {}

        for key, value in self._config.items():
            if key.endswith("_encrypted"):
                try:
                    self.encryption.decrypt(value)
                    verification_results[key] = True
                except Exception as e:
                    verification_results[key] = False
                    logger.error(
                        f"❌ Verification failed for {key}", error=str(e)
                    )

        logger.info(
            f"✅ Configuration verification complete",
            valid=sum(verification_results.values()),
            total=len(verification_results),
        )

        return verification_results


# Global secure config instance
_secure_config = None


def get_secure_config() -> SecureConfig:
    """Get or create global SecureConfig instance"""
    global _secure_config
    if _secure_config is None:
        _secure_config = SecureConfig()
    return _secure_config


def initialize_secure_config_from_env() -> SecureConfig:
    """
    Initialize SecureConfig from environment variables

    Reads credentials from:
    - POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_DATABASE
    - TDENGINE_HOST, TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_PORT, TDENGINE_DATABASE
    - JWT_SECRET_KEY

    Returns:
        Initialized SecureConfig instance

    SECURITY: Reads from environment variables, encrypts before storage
    """
    config = SecureConfig()

    # PostgreSQL credentials
    if os.getenv("POSTGRESQL_HOST"):
        config.set_database_credentials(
            db_type="postgresql",
            host=os.getenv("POSTGRESQL_HOST"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            user=os.getenv("POSTGRESQL_USER"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
            database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        )
        logger.info("✅ PostgreSQL credentials configured")

    # TDengine credentials
    if os.getenv("TDENGINE_HOST"):
        config.set_database_credentials(
            db_type="tdengine",
            host=os.getenv("TDENGINE_HOST"),
            port=int(os.getenv("TDENGINE_PORT", "6030")),
            user=os.getenv("TDENGINE_USER"),
            password=os.getenv("TDENGINE_PASSWORD"),
            database=os.getenv("TDENGINE_DATABASE", "market_data"),
        )
        logger.info("✅ TDengine credentials configured")

    # JWT secret
    if os.getenv("JWT_SECRET_KEY"):
        config.set_jwt_secret(os.getenv("JWT_SECRET_KEY"))
        logger.info("✅ JWT secret configured")

    return config
