"""
Unified Exception Handling - Decorator pattern for API endpoints
Task 1.4: Remove Duplicate Code - Phase 1

Consolidates 100+ duplicate try/except blocks from 20+ API endpoint files.

BEFORE (in each API endpoint):
```python
@router.get("/data")
async def get_data():
    try:
        data = await fetch_data()
        return {"status": "success", "data": data}
    except ValueError as e:
        logger.error("Invalid input", error=str(e))
        return {"error": "Invalid input", "message": str(e)}, 400
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        return {"error": "Internal error", "message": str(e)}, 500
```

AFTER (use decorator):
```python
@router.get("/data")
@handle_exceptions
async def get_data():
    data = await fetch_data()
    return {"status": "success", "data": data}
```

Estimated Duplication Reduced: 200+ lines
"""

import functools
import inspect
from typing import Any, Callable, Dict

import structlog
from fastapi import HTTPException

logger = structlog.get_logger()


def handle_exceptions(
    func: Callable = None,
    *,
    include_traceback: bool = False,
    default_status: int = 500,
    error_key: str = "error",
    message_key: str = "message",
):
    """
    Decorator for unified exception handling in API endpoints

    Automatically catches and logs exceptions, returns standardized error responses.

    Args:
        func: Function to decorate (when used without parentheses)
        include_traceback: Include traceback in error response (dev only)
        default_status: Default HTTP status code for unhandled exceptions
        error_key: Key for error name in response
        message_key: Key for error message in response

    Usage:
        ```python
        @router.get("/data")
        @handle_exceptions
        async def get_data():
            return await fetch_data()

        @router.post("/data")
        @handle_exceptions(include_traceback=True)  # For development
        def create_data(data):
            return save_data(data)
        ```

    Returns:
        Standardized error response on exception
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        async def async_wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                return await f(*args, **kwargs)
            except HTTPException as e:
                # FastAPI HTTPException - reraise to preserve status code
                logger.warning(
                    f"HTTP exception in {f.__name__}",
                    status_code=e.status_code,
                    message=e.detail,
                )
                raise

            except ValueError as e:
                logger.warning("Validation error in {f.__name__}", error=str(e))
                return {
                    error_key: "Validation Error",
                    message_key: str(e),
                }, 400

            except KeyError as e:
                logger.warning("Missing required parameter in {f.__name__}", error=str(e))
                return {
                    error_key: "Missing Required Parameter",
                    message_key: f"Required parameter not found: {str(e)}",
                }, 400

            except PermissionError as e:
                logger.warning("Permission denied in {f.__name__}", error=str(e))
                return {
                    error_key: "Permission Denied",
                    message_key: str(e),
                }, 403

            except Exception as e:
                logger.error(
                    f"Unhandled exception in {f.__name__}",
                    error=str(e),
                    exc_info=e,
                )
                response = {
                    error_key: "Internal Server Error",
                    message_key: "An unexpected error occurred",
                }

                if include_traceback:
                    import traceback

                    response["traceback"] = traceback.format_exc()

                return response, default_status

        @functools.wraps(f)
        def sync_wrapper(*args, **kwargs) -> Dict[str, Any]:
            try:
                return f(*args, **kwargs)
            except HTTPException as e:
                logger.warning(
                    f"HTTP exception in {f.__name__}",
                    status_code=e.status_code,
                    message=e.detail,
                )
                raise

            except ValueError as e:
                logger.warning("Validation error in {f.__name__}", error=str(e))
                return {
                    error_key: "Validation Error",
                    message_key: str(e),
                }, 400

            except KeyError as e:
                logger.warning("Missing required parameter in {f.__name__}", error=str(e))
                return {
                    error_key: "Missing Required Parameter",
                    message_key: f"Required parameter not found: {str(e)}",
                }, 400

            except PermissionError as e:
                logger.warning("Permission denied in {f.__name__}", error=str(e))
                return {
                    error_key: "Permission Denied",
                    message_key: str(e),
                }, 403

            except Exception as e:
                logger.error(
                    f"Unhandled exception in {f.__name__}",
                    error=str(e),
                    exc_info=e,
                )
                response = {
                    error_key: "Internal Server Error",
                    message_key: "An unexpected error occurred",
                }

                if include_traceback:
                    import traceback

                    response["traceback"] = traceback.format_exc()

                return response, default_status

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(f):
            return async_wrapper
        else:
            return sync_wrapper

    # Support both @handle_exceptions and @handle_exceptions(...)
    if func is not None:
        return decorator(func)
    else:
        return decorator


def handle_validation_errors(func: Callable) -> Callable:
    """
    Specialized decorator for validation-heavy endpoints

    Catches only validation errors (ValueError, KeyError) and returns 400.
    Other exceptions are logged as warnings and re-raised.

    Usage:
        ```python
        @router.post("/validate")
        @handle_validation_errors
        def validate_input(data):
            if not data:
                raise ValueError("Data required")
            return {"valid": True}
        ```
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (ValueError, KeyError) as e:
            logger.warning("Validation error in {func.__name__}", error=str(e))
            return {"error": "Validation Error", "message": str(e)}, 400

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError) as e:
            logger.warning("Validation error in {func.__name__}", error=str(e))
            return {"error": "Validation Error", "message": str(e)}, 400

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def handle_database_errors(func: Callable) -> Callable:
    """
    Specialized decorator for database-heavy endpoints

    Catches database errors and returns 503 Service Unavailable.

    Usage:
        ```python
        @router.get("/data")
        @handle_database_errors
        def get_data():
            return query_database()
        ```
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["database", "connection", "query", "sql"]):
                logger.error("Database error in {func.__name__}", error=str(e))
                return {
                    "error": "Database Error",
                    "message": "Database connection failed",
                }, 503
            else:
                raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["database", "connection", "query", "sql"]):
                logger.error("Database error in {func.__name__}", error=str(e))
                return {
                    "error": "Database Error",
                    "message": "Database connection failed",
                }, 503
            else:
                raise

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
