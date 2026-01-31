"""
Standardized Response Schemas - Eliminate duplicate response formatting
Task 1.4: Remove Duplicate Code - Phase 1

Consolidates 80+ duplicate response dict constructions from 35+ API endpoints.

BEFORE (in each endpoint):
```python
@router.get("/data")
def get_data():
    data = fetch_data()
    return {
        "status": "success",
        "code": 200,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
```

AFTER (use schema):
```python
@router.get("/data")
def get_data():
    data = fetch_data()
    return APIResponse.success(data=data)
```

Estimated Duplication Reduced: 80+ lines
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class APIResponse:
    """
    Standardized API response builder

    Ensures all API responses follow consistent format across all endpoints.

    Response Format:
        ```json
        {
            "status": "success|error",
            "code": 200,
            "message": "Operation successful",
            "data": {...},
            "timestamp": "2024-01-01T00:00:00.000Z"
        }
        ```
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        code: int = 200,
    ) -> Dict[str, Any]:
        """
        Build successful response

        Args:
            data: Response data
            message: Success message
            code: HTTP status code

        Returns:
            Standardized success response dict
        """
        return {
            "status": "success",
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def error(
        error: str,
        message: str = "An error occurred",
        code: int = 500,
        details: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Build error response

        Args:
            error: Error type/name
            message: Error message
            code: HTTP status code
            details: Additional error details

        Returns:
            Standardized error response dict
        """
        response = {
            "status": "error",
            "code": code,
            "error": error,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if details:
            response["details"] = details

        return response

    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        errors: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Build validation error response

        Args:
            message: Error message
            errors: Field validation errors

        Returns:
            Standardized validation error response
        """
        return APIResponse.error(
            error="Validation Error",
            message=message,
            code=400,
            details=errors,
        )

    @staticmethod
    def not_found(
        resource: str = "Resource",
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build not found (404) response

        Args:
            resource: Name of resource not found
            message: Custom message

        Returns:
            Standardized 404 response
        """
        msg = message or f"{resource} not found"
        return APIResponse.error(
            error="Not Found",
            message=msg,
            code=404,
        )

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> Dict[str, Any]:
        """
        Build unauthorized (401) response

        Args:
            message: Error message

        Returns:
            Standardized 401 response
        """
        return APIResponse.error(
            error="Unauthorized",
            message=message,
            code=401,
        )

    @staticmethod
    def forbidden(message: str = "Forbidden") -> Dict[str, Any]:
        """
        Build forbidden (403) response

        Args:
            message: Error message

        Returns:
            Standardized 403 response
        """
        return APIResponse.error(
            error="Forbidden",
            message=message,
            code=403,
        )

    @staticmethod
    def server_error(message: str = "Internal server error") -> Dict[str, Any]:
        """
        Build server error (500) response

        Args:
            message: Error message

        Returns:
            Standardized 500 response
        """
        return APIResponse.error(
            error="Internal Server Error",
            message=message,
            code=500,
        )

    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "Data retrieved successfully",
    ) -> Dict[str, Any]:
        """
        Build paginated response

        Args:
            items: List of items
            total: Total item count
            page: Current page number
            page_size: Items per page
            message: Response message

        Returns:
            Standardized paginated response
        """
        return APIResponse.success(
            data={
                "items": items,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "pages": (total + page_size - 1) // page_size,
                },
            },
            message=message,
        )


# Pydantic models for response validation (optional, for strict typing)


class SuccessResponseModel(BaseModel):
    """Pydantic model for success responses"""

    status: str = Field(default="success", description="Response status")
    code: int = Field(default=200, description="HTTP status code")
    message: str = Field(description="Response message")
    data: Any = Field(default=None, description="Response data")
    timestamp: str = Field(description="Response timestamp")


class ErrorResponseModel(BaseModel):
    """Pydantic model for error responses"""

    status: str = Field(default="error", description="Response status")
    code: int = Field(description="HTTP status code")
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict] = Field(default=None, description="Error details")
    timestamp: str = Field(description="Response timestamp")


# Usage examples and best practices

"""
USAGE EXAMPLES:

1. Simple success response:
    ```python
    @router.get("/users/{user_id}")
    def get_user(user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return APIResponse.not_found("User"), 404
        return APIResponse.success(data=user.to_dict())
    ```

2. Validation error:
    ```python
    @router.post("/users")
    def create_user(user_data: dict):
        errors = validate_user_data(user_data)
        if errors:
            return APIResponse.validation_error(errors=errors), 400
        user = db.create_user(user_data)
        return APIResponse.success(data=user.to_dict(), code=201), 201
    ```

3. Paginated response:
    ```python
    @router.get("/users")
    def list_users(page: int = 1, page_size: int = 20):
        query = db.query(User)
        total = query.count()
        items = query.offset((page-1)*page_size).limit(page_size).all()
        return APIResponse.paginated(
            items=[u.to_dict() for u in items],
            total=total,
            page=page,
            page_size=page_size
        )
    ```

4. With exception handling:
    ```python
    @router.get("/data")
    @handle_exceptions
    def get_data():
        data = fetch_expensive_data()
        return APIResponse.success(data=data)
    ```
"""
