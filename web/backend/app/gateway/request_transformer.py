"""
Request/Response Transformer - Request and response transformation middleware

Handles request validation, transformation, and response formatting.

Task 11: API Gateway and Request Routing
Author: Claude Code
Date: 2025-11-07
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class RequestMetadata:
    """Metadata for a request"""

    correlation_id: str
    request_time: datetime
    client_ip: str
    user_agent: Optional[str] = None
    version: str = "v1"


class RequestTransformer:
    """Transformer for incoming requests"""

    def __init__(self):
        """Initialize request transformer"""
        logger.info("✅ Request Transformer initialized")

    def transform(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Transform incoming request

        Args:
            path: Request path
            method: HTTP method
            headers: Request headers
            body: Request body
            query_params: Query parameters

        Returns:
            Transformed request dictionary
        """
        # Extract version from path
        version = self._extract_version(path)

        # Generate correlation ID
        correlation_id = headers.get(
            "X-Correlation-ID",
            self._generate_correlation_id(),
        )

        # Create metadata
        metadata = RequestMetadata(
            correlation_id=correlation_id,
            request_time=datetime.now(timezone.utc),
            client_ip=headers.get("X-Forwarded-For", "unknown"),
            user_agent=headers.get("User-Agent"),
            version=version,
        )

        # Normalize path
        normalized_path = self._normalize_path(path)

        # Validate and sanitize body
        validated_body = self._validate_body(body) if body else None

        # Validate and sanitize query params
        validated_params = self._validate_query_params(query_params) if query_params else None

        return {
            "path": normalized_path,
            "method": method.upper(),
            "headers": headers,
            "body": validated_body,
            "query_params": validated_params,
            "metadata": {
                "correlation_id": metadata.correlation_id,
                "request_time": metadata.request_time.isoformat(),
                "client_ip": metadata.client_ip,
                "user_agent": metadata.user_agent,
                "version": metadata.version,
            },
        }

    def _extract_version(self, path: str) -> str:
        """Extract API version from path

        Args:
            path: Request path

        Returns:
            Version string (e.g., "v1")
        """
        # Extract version like /api/v1/... or /api/v2/...
        parts = path.split("/")
        for part in parts:
            if part.startswith("v") and part[1:].isdigit():
                return part

        return "v1"

    def _normalize_path(self, path: str) -> str:
        """Normalize request path

        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        # Remove trailing slash
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]

        # Ensure leading slash
        if not path.startswith("/"):
            path = f"/{path}"

        return path

    def _validate_body(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize request body

        Args:
            body: Request body

        Returns:
            Validated body
        """
        if not isinstance(body, dict):
            logger.warning("⚠️ Request body is not a dictionary")
            return {}

        # Basic validation - can be extended
        return body

    def _validate_query_params(self, params: Dict[str, str]) -> Dict[str, str]:
        """Validate and sanitize query parameters

        Args:
            params: Query parameters

        Returns:
            Validated parameters
        """
        if not isinstance(params, dict):
            return {}

        # Remove empty parameters
        return {k: v for k, v in params.items() if v}

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID

        Returns:
            Correlation ID
        """
        from uuid import uuid4

        return str(uuid4())


class ResponseTransformer:
    """Transformer for outgoing responses"""

    def __init__(self):
        """Initialize response transformer"""
        logger.info("✅ Response Transformer initialized")

    def transform(
        self,
        data: Any,
        status_code: int = 200,
        correlation_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transform outgoing response

        Args:
            data: Response data
            status_code: HTTP status code
            correlation_id: Request correlation ID
            error: Error message if applicable

        Returns:
            Transformed response dictionary
        """
        response = {
            "success": 200 <= status_code < 300,
            "status_code": status_code,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if correlation_id:
            response["correlation_id"] = correlation_id

        if error:
            response["error"] = error

        return response

    def transform_error(
        self,
        status_code: int,
        error_message: str,
        error_type: str = "unknown",
        correlation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Transform error response

        Args:
            status_code: HTTP status code
            error_message: Error message
            error_type: Type of error
            correlation_id: Request correlation ID
            details: Additional error details

        Returns:
            Error response dictionary
        """
        response = {
            "success": False,
            "status_code": status_code,
            "error": error_message,
            "error_type": error_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if correlation_id:
            response["correlation_id"] = correlation_id

        if details:
            response["details"] = details

        return response

    def transform_list(
        self,
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transform paginated list response

        Args:
            items: List of items
            total: Total number of items
            page: Current page number
            page_size: Page size
            correlation_id: Request correlation ID

        Returns:
            Paginated response dictionary
        """
        total_pages = (total + page_size - 1) // page_size

        response = {
            "success": True,
            "status_code": 200,
            "data": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if correlation_id:
            response["correlation_id"] = correlation_id

        return response


class RequestValidationError(Exception):
    """Request validation error"""

    def __init__(self, message: str, field: Optional[str] = None):
        """Initialize validation error

        Args:
            message: Error message
            field: Field that failed validation
        """
        self.message = message
        self.field = field
        super().__init__(message)


class RequestValidator:
    """Validator for request data"""

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that required fields are present

        Args:
            data: Data dictionary
            required_fields: List of required field names

        Raises:
            RequestValidationError: If required fields are missing
        """
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise RequestValidationError(f"Missing required fields: {', '.join(missing)}")

    @staticmethod
    def validate_field_type(data: Dict[str, Any], field: str, expected_type: type) -> None:
        """Validate field type

        Args:
            data: Data dictionary
            field: Field name
            expected_type: Expected type

        Raises:
            RequestValidationError: If type doesn't match
        """
        if field not in data:
            return

        if not isinstance(data[field], expected_type):
            raise RequestValidationError(
                f"Field '{field}' should be {expected_type.__name__}",
                field=field,
            )

    @staticmethod
    def validate_field_range(
        data: Dict[str, Any],
        field: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> None:
        """Validate numeric field range

        Args:
            data: Data dictionary
            field: Field name
            min_value: Minimum value
            max_value: Maximum value

        Raises:
            RequestValidationError: If value is out of range
        """
        if field not in data:
            return

        value = data[field]
        if min_value is not None and value < min_value:
            raise RequestValidationError(f"Field '{field}' must be >= {min_value}", field=field)
        if max_value is not None and value > max_value:
            raise RequestValidationError(f"Field '{field}' must be <= {max_value}", field=field)

    @staticmethod
    def validate_choices(data: Dict[str, Any], field: str, choices: List[Any]) -> None:
        """Validate field is one of allowed choices

        Args:
            data: Data dictionary
            field: Field name
            choices: Allowed choices

        Raises:
            RequestValidationError: If value is not in choices
        """
        if field not in data:
            return

        if data[field] not in choices:
            raise RequestValidationError(
                f"Field '{field}' must be one of {choices}",
                field=field,
            )
