"""
Database access modules for MyStocks API
Provides repositories for data access with proper error handling
"""

from sqlalchemy.ext.declarative import declarative_base

from app.db.user_repository import UserRepository

# Unified SQLAlchemy Base for all ORM models
# Used by tests to create in-memory database tables
Base = declarative_base()

__all__ = ["UserRepository", "Base"]
