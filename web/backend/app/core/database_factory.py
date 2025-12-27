"""
Database Factory - Centralized database connection management
Task 1.4: Remove Duplicate Code - Phase 1

Consolidates duplicate database connection initialization patterns
across 9+ service files into a single factory pattern.

BEFORE: Each service had its own _build_db_url() and connection setup
AFTER: Single factory pattern used by all services

Estimated Duplication Reduced: 150+ lines
"""

import os
from typing import Optional, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import structlog

logger = structlog.get_logger()


class DatabaseFactory:
    """
    Factory for creating database connections and sessions

    Consolidates duplicate database URL building and connection initialization
    that was repeated in 9+ service files.

    BEFORE (in each service):
    ```python
    def _build_db_url():
        host = os.getenv("POSTGRESQL_HOST", "192.168.123.104")
        port = os.getenv("POSTGRESQL_PORT", "5438")
        user = os.getenv("POSTGRESQL_USER", "postgres")
        password = os.getenv("POSTGRESQL_PASSWORD", "c790414J")
        database = os.getenv("POSTGRESQL_DATABASE", "mystocks")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    ```

    AFTER (use factory):
    ```python
    engine, SessionLocal = DatabaseFactory.create_postgresql()
    ```
    """

    _engines = {}  # Cache engines to avoid recreating
    _session_factories = {}

    @staticmethod
    def create_postgresql(
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
    ) -> Tuple:
        """
        Create PostgreSQL database engine and session factory

        Args:
            host: Database host (reads from POSTGRESQL_HOST env var if not provided)
            port: Database port (reads from POSTGRESQL_PORT env var if not provided)
            user: Database user (reads from POSTGRESQL_USER env var if not provided)
            password: Database password (reads from POSTGRESQL_PASSWORD env var if not provided)
            database: Database name (reads from POSTGRESQL_DATABASE env var if not provided)
            pool_size: Connection pool size
            max_overflow: Max overflow connections

        Returns:
            Tuple of (engine, SessionLocal)

        SECURITY: Use environment variables for credentials, never hardcode
        """
        # Get credentials from environment or use defaults
        host = host or os.getenv("POSTGRESQL_HOST", "192.168.123.104")
        port = port or int(os.getenv("POSTGRESQL_PORT", "5438"))
        user = user or os.getenv("POSTGRESQL_USER", "postgres")
        password = password or os.getenv("POSTGRESQL_PASSWORD")
        database = database or os.getenv("POSTGRESQL_DATABASE", "mystocks")

        # Build connection URL
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        # Create engine with connection pooling
        engine = create_engine(
            url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=False,
        )

        # Create session factory
        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

        logger.info(
            "✅ PostgreSQL connection pool created",
            host=host,
            port=port,
            database=database,
            pool_size=pool_size,
        )

        # Cache for reuse
        DatabaseFactory._engines["postgresql"] = engine
        DatabaseFactory._session_factories["postgresql"] = SessionLocal

        return engine, SessionLocal

    @staticmethod
    def create_mysql(
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        pool_size: int = 10,
        max_overflow: int = 20,
    ) -> Tuple:
        """
        Create MySQL database engine and session factory

        Args:
            host: Database host
            port: Database port
            user: Database user
            password: Database password
            database: Database name
            pool_size: Connection pool size
            max_overflow: Max overflow connections

        Returns:
            Tuple of (engine, SessionLocal)
        """
        host = host or os.getenv("MYSQL_HOST", "192.168.123.104")
        port = port or int(os.getenv("MYSQL_PORT", "3306"))
        user = user or os.getenv("MYSQL_USER", "root")
        password = password or os.getenv("MYSQL_PASSWORD")
        database = database or os.getenv("MYSQL_DATABASE", "mystocks")

        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(
            url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=False,
        )

        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

        logger.info(
            "✅ MySQL connection pool created",
            host=host,
            port=port,
            database=database,
        )

        DatabaseFactory._engines["mysql"] = engine
        DatabaseFactory._session_factories["mysql"] = SessionLocal

        return engine, SessionLocal

    @staticmethod
    def get_session(db_type: str = "postgresql") -> Session:
        """
        Get a new database session

        Args:
            db_type: Type of database (postgresql, mysql)

        Returns:
            Database session

        Raises:
            KeyError: If database type not initialized
        """
        if db_type not in DatabaseFactory._session_factories:
            raise KeyError(f"Database type '{db_type}' not initialized. " f"Call create_{db_type}() first.")

        return DatabaseFactory._session_factories[db_type]()

    @staticmethod
    def close_all():
        """Close all database engines and connections"""
        for db_type, engine in DatabaseFactory._engines.items():
            engine.dispose()
            logger.info(f"✅ Closed {db_type} connection pool")

        DatabaseFactory._engines.clear()
        DatabaseFactory._session_factories.clear()


# Convenience functions for common usage
_postgresql_engine = None
_postgresql_session = None


def get_postgresql_engine():
    """Get or create PostgreSQL engine (singleton pattern)"""
    global _postgresql_engine, _postgresql_session

    if _postgresql_engine is None:
        _postgresql_engine, _postgresql_session = DatabaseFactory.create_postgresql()

    return _postgresql_engine


def get_postgresql_session() -> Session:
    """Get a PostgreSQL session (singleton engine)"""
    engine = get_postgresql_engine()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()
