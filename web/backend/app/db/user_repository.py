"""
User Database Repository
Handles all user-related database operations with proper error handling
"""

from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import UserInDB


# 简化的异常类（如果需要更详细的异常处理）
class DatabaseConnectionError(Exception):
    """数据库连接错误"""

    pass


class DatabaseOperationError(Exception):
    """数据库操作错误"""

    pass


class DataValidationError(Exception):
    """数据验证错误"""

    pass


class UserRepository:
    """User repository with database access and error handling"""

    def __init__(self, session: Session):
        """
        Initialize user repository with database session

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """
        Retrieve user from database by username

        Args:
            username: Username to look up

        Returns:
            UserInDB object if found, None otherwise

        Raises:
            DatabaseConnectionError: If database connection fails
            DataValidationError: If username is invalid
            DatabaseOperationError: If query execution fails
        """
        if not username or not isinstance(username, str):
            raise DataValidationError(
                message="Username must be a non-empty string",
                code="INVALID_USERNAME",
                severity="HIGH",
            )

        try:
            # Query users table for username
            query = text(
                """
                SELECT id, username, email, hashed_password, role, is_active
                FROM users
                WHERE username = :username AND is_active = true
                LIMIT 1
                """
            )

            result = self.session.execute(query, {"username": username}).fetchone()

            if result is None:
                return None

            # Convert result tuple to UserInDB object
            return UserInDB(
                id=result[0],
                username=result[1],
                email=result[2],
                hashed_password=result[3],
                role=result[4],
                is_active=result[5],
            )

        except SQLAlchemyError as e:
            if "connection" in str(e).lower():
                raise DatabaseConnectionError(
                    message=f"Failed to connect to database when looking up user: {str(e)}",
                    code="DB_CONNECTION_FAILED",
                    severity="CRITICAL",
                    original_exception=e,
                )
            else:
                raise DatabaseOperationError(
                    message=f"Database query failed for user lookup: {str(e)}",
                    code="DB_QUERY_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

    def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        """
        Retrieve user from database by ID

        Args:
            user_id: User ID to look up

        Returns:
            UserInDB object if found, None otherwise

        Raises:
            DatabaseConnectionError: If database connection fails
            DataValidationError: If user_id is invalid
            DatabaseOperationError: If query execution fails
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise DataValidationError(
                message="User ID must be a positive integer",
                code="INVALID_USER_ID",
                severity="HIGH",
            )

        try:
            query = text(
                """
                SELECT id, username, email, hashed_password, role, is_active
                FROM users
                WHERE id = :user_id AND is_active = true
                LIMIT 1
                """
            )

            result = self.session.execute(query, {"user_id": user_id}).fetchone()

            if result is None:
                return None

            return UserInDB(
                id=result[0],
                username=result[1],
                email=result[2],
                hashed_password=result[3],
                role=result[4],
                is_active=result[5],
            )

        except SQLAlchemyError as e:
            if "connection" in str(e).lower():
                raise DatabaseConnectionError(
                    message=f"Failed to connect to database when looking up user by ID: {str(e)}",
                    code="DB_CONNECTION_FAILED",
                    severity="CRITICAL",
                    original_exception=e,
                )
            else:
                raise DatabaseOperationError(
                    message=f"Database query failed for user lookup by ID: {str(e)}",
                    code="DB_QUERY_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Retrieve user from database by email

        Args:
            email: Email address to look up

        Returns:
            UserInDB object if found, None otherwise

        Raises:
            DatabaseConnectionError: If database connection fails
            DataValidationError: If email is invalid
            DatabaseOperationError: If query execution fails
        """
        if not email or "@" not in email:
            raise DataValidationError(
                message="Email must be a valid email address",
                code="INVALID_EMAIL",
                severity="HIGH",
            )

        try:
            query = text(
                """
                SELECT id, username, email, hashed_password, role, is_active
                FROM users
                WHERE email = :email AND is_active = true
                LIMIT 1
                """
            )

            result = self.session.execute(query, {"email": email}).fetchone()

            if result is None:
                return None

            return UserInDB(
                id=result[0],
                username=result[1],
                email=result[2],
                hashed_password=result[3],
                role=result[4],
                is_active=result[5],
            )

        except SQLAlchemyError as e:
            if "connection" in str(e).lower():
                raise DatabaseConnectionError(
                    message=f"Failed to connect to database when looking up user by email: {str(e)}",
                    code="DB_CONNECTION_FAILED",
                    severity="CRITICAL",
                    original_exception=e,
                )
            else:
                raise DatabaseOperationError(
                    message=f"Database query failed for user lookup by email: {str(e)}",
                    code="DB_QUERY_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

    def get_all_users(self) -> List[UserInDB]:
        """
        Retrieve all active users from database

        Returns:
            List of UserInDB objects

        Raises:
            DatabaseConnectionError: If database connection fails
            DatabaseOperationError: If query execution fails
        """
        try:
            query = text(
                """
                SELECT id, username, email, hashed_password, role, is_active
                FROM users
                WHERE is_active = true
                ORDER BY username ASC
                """
            )

            results = self.session.execute(query).fetchall()

            return [
                UserInDB(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    hashed_password=row[3],
                    role=row[4],
                    is_active=row[5],
                )
                for row in results
            ]

        except SQLAlchemyError as e:
            if "connection" in str(e).lower():
                raise DatabaseConnectionError(
                    message=f"Failed to connect to database when retrieving users: {str(e)}",
                    code="DB_CONNECTION_FAILED",
                    severity="CRITICAL",
                    original_exception=e,
                )
            else:
                raise DatabaseOperationError(
                    message=f"Database query failed for users retrieval: {str(e)}",
                    code="DB_QUERY_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

    def log_user_action(
        self,
        user_id: Optional[int],
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> bool:
        """
        Log user action to audit log table

        Args:
            user_id: User ID (optional, for failed logins)
            action: Action type (login, logout, password_reset, etc.)
            ip_address: Client IP address
            user_agent: Client user agent string
            details: Additional details as dictionary

        Returns:
            True if logging succeeded, False otherwise
        """
        try:
            insert_query = text(
                """
                INSERT INTO user_audit_log (user_id, action, ip_address, user_agent, details)
                VALUES (:user_id, :action, :ip_address, :user_agent, :details)
                """
            )

            self.session.execute(
                insert_query,
                {
                    "user_id": user_id,
                    "action": action,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "details": details,
                },
            )
            self.session.commit()
            return True

        except Exception as e:
            # Log but don't raise - audit logging should not block authentication
            print(f"Warning: Failed to log user action: {str(e)}")
            self.session.rollback()
            return False

    def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: str = "user",
        is_active: bool = True,
    ) -> UserInDB:
        """
        Create a new user in the database

        Args:
            username: Username (must be unique)
            email: Email address (must be unique)
            hashed_password: Bcrypt hashed password
            role: User role (default: "user")
            is_active: Whether user is active (default: True)

        Returns:
            UserInDB: Created user object

        Raises:
            DataValidationError: If input data is invalid
            DatabaseOperationError: If username/email already exists or query fails
            DatabaseConnectionError: If database connection fails
        """
        # Validate input
        if not username or not isinstance(username, str):
            raise DataValidationError(
                message="Username must be a non-empty string",
                code="INVALID_USERNAME",
                severity="HIGH",
            )

        if not email or "@" not in email:
            raise DataValidationError(
                message="Email must be a valid email address",
                code="INVALID_EMAIL",
                severity="HIGH",
            )

        if not hashed_password or not isinstance(hashed_password, str):
            raise DataValidationError(
                message="Hashed password must be a non-empty string",
                code="INVALID_PASSWORD",
                severity="HIGH",
            )

        if role not in ["user", "admin"]:
            raise DataValidationError(
                message="Role must be either 'user' or 'admin'",
                code="INVALID_ROLE",
                severity="HIGH",
            )

        try:
            # Check if username already exists
            existing_user = self.get_user_by_username(username)
            if existing_user:
                raise DatabaseOperationError(
                    message=f"Username '{username}' already exists",
                    code="USERNAME_EXISTS",
                    severity="MEDIUM",
                )

            # Check if email already exists
            existing_email = self.get_user_by_email(email)
            if existing_email:
                raise DatabaseOperationError(
                    message=f"Email '{email}' already exists",
                    code="EMAIL_EXISTS",
                    severity="MEDIUM",
                )

            # Insert new user
            insert_query = text(
                """
                INSERT INTO users (username, email, hashed_password, role, is_active)
                VALUES (:username, :email, :hashed_password, :role, :is_active)
                RETURNING id, username, email, hashed_password, role, is_active
                """
            )

            result = self.session.execute(
                insert_query,
                {
                    "username": username,
                    "email": email,
                    "hashed_password": hashed_password,
                    "role": role,
                    "is_active": is_active,
                },
            ).fetchone()

            self.session.commit()

            # Return created user
            return UserInDB(
                id=result[0],
                username=result[1],
                email=result[2],
                hashed_password=result[3],
                role=result[4],
                is_active=result[5],
            )

        except DatabaseOperationError:
            # Re-raise our custom errors
            self.session.rollback()
            raise

        except SQLAlchemyError as e:
            self.session.rollback()
            if "connection" in str(e).lower():
                raise DatabaseConnectionError(
                    message=f"Failed to connect to database when creating user: {str(e)}",
                    code="DB_CONNECTION_FAILED",
                    severity="CRITICAL",
                    original_exception=e,
                )
            else:
                raise DatabaseOperationError(
                    message=f"Database query failed for user creation: {str(e)}",
                    code="DB_QUERY_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

        except Exception as e:
            self.session.rollback()
            raise DatabaseOperationError(
                message=f"Unexpected error during user creation: {str(e)}",
                code="USER_CREATION_FAILED",
                severity="HIGH",
                original_exception=e,
            )
