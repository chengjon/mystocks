"""
Contract Validation Middleware

Validates API responses against OpenAPI specification schema.
Prevents "contract drift" by ensuring backend responses match the contract.
"""

import logging
from typing import Any, Dict, List, Optional

from jsonschema import Draft7Validator, ValidationError, validate
from jsonschema.exceptions import best_match

logger = logging.getLogger(__name__)


class ContractValidator:
    """
    OpenAPI Contract Validator

    Validates API responses against OpenAPI specification schemas.
    Similar to Schemathesis but implemented in pure Python.
    """

    def __init__(self, openapi_spec: Dict[str, Any]):
        """
        Initialize validator with OpenAPI specification

        Args:
            openapi_spec: Parsed OpenAPI specification dictionary
        """
        self.spec = openapi_spec
        self.schemas = self._extract_schemas()
        self._cache = {}

    def _extract_schemas(self) -> Dict[str, Any]:
        """Extract all schemas from OpenAPI spec"""
        schemas = {}

        # Handle components.schemas
        components = self.spec.get("components", {})
        if "schemas" in components:
            for name, schema in components["schemas"].items():
                schemas[name] = schema
                schemas[f"#/components/schemas/{name}"] = schema

        # Handle inline schemas in paths
        for path, path_item in self.spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    responses = operation.get("responses", {})
                    for code, response in responses.items():
                        content = response.get("content", {})
                        if "application/json" in content:
                            schema = content["application/json"].get("schema", {})
                            if "$ref" in schema:
                                ref = schema["$ref"]
                                ref_path = ref.replace("#/", "").split("/")
                                schemas[ref] = self._resolve_ref(ref_path)
                            elif "properties" in schema:
                                schemas[f"inline_{path}_{method}_{code}"] = schema

        return schemas

    def _resolve_ref(self, ref_path: List[str]) -> Optional[Dict[str, Any]]:
        """Resolve JSON reference"""
        current = self.spec
        for part in ref_path:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def get_response_schema(self, path: str, method: str, status_code: str = "200") -> Optional[Dict[str, Any]]:
        """
        Get response schema for a specific endpoint

        Args:
            path: API path (e.g., "/api/users")
            method: HTTP method (GET, POST, etc.)
            status_code: Response status code

        Returns:
            Schema dictionary or None if not found
        """
        key = f"{method.upper()}_{path}_{status_code}"
        if key in self._cache:
            return self._cache[key]

        path_item = self.spec.get("paths", {}).get(path, {})
        operation = path_item.get(method.upper(), {})
        responses = operation.get("responses", {})
        response = responses.get(status_code, responses.get("default", {}))

        content = response.get("content", {})
        if "application/json" not in content:
            self._cache[key] = None
            return None

        schema = content["application/json"].get("schema", {})
        resolved_schema = self._resolve_schema(schema)

        self._cache[key] = resolved_schema
        return resolved_schema

    def _resolve_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve schema references and build complete schema"""
        if "$ref" in schema:
            ref = schema["$ref"]
            ref_path = ref.replace("#/", "").split("/")
            return self._resolve_ref(ref_path) or schema

        # Handle allOf, anyOf, oneOf
        resolved = {}
        for key, value in schema.items():
            if key == "allOf":
                resolved[key] = [self._resolve_schema(v) for v in value]
            elif key == "anyOf":
                resolved[key] = [self._resolve_schema(v) for v in value]
            elif key == "oneOf":
                resolved[key] = [self._resolve_schema(v) for v in value]
            elif key == "items":
                resolved[key] = self._resolve_schema(value)
            elif key == "properties":
                resolved[key] = {k: self._resolve_schema(v) for k, v in value.items()}
            elif key == "additionalProperties":
                if isinstance(value, dict):
                    resolved[key] = self._resolve_schema(value)
                else:
                    resolved[key] = value
            else:
                resolved[key] = value

        return resolved

    def validate_response(self, path: str, method: str, status_code: str, response_data: Any) -> "ValidationResult":
        """
        Validate API response against contract

        Args:
            path: API path
            method: HTTP method
            status_code: Response status code
            response_data: Response body to validate

        Returns:
            ValidationResult with success status and details
        """
        schema = self.get_response_schema(path, method, status_code)

        if schema is None:
            return ValidationResult(
                success=True,
                warnings=["No schema defined for this response"],
                schema_path=f"{method.upper()} {path} {status_code}",
            )

        try:
            validate(instance=response_data, schema=schema, cls=Draft7Validator)
            return ValidationResult(success=True, schema_path=f"{method.upper()} {path} {status_code}")
        except ValidationError as e:
            error_path = ".".join(str(p) for p in e.path) if e.path else "root"
            best_error = best_match(e.context) if e.context else e

            return ValidationResult(
                success=False,
                errors=[f"Path: {error_path}, Error: {best_error.message}"],
                schema_path=f"{method.upper()} {path} {status_code}",
            )

    def get_endpoint_schema_paths(self) -> List[Dict[str, Any]]:
        """Get all endpoint schema paths for testing"""
        endpoints = []
        for path, path_item in self.spec.get("paths", {}).items():
            for method in ["get", "post", "put", "delete", "patch"]:
                if method in path_item:
                    operation = path_item[method]
                    operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_')}")
                    summary = operation.get("summary", "")
                    description = operation.get("description", "")

                    responses = operation.get("responses", {})
                    response_schemas = {}
                    for code, response in responses.items():
                        content = response.get("content", {})
                        if "application/json" in content:
                            schema = content["application/json"].get("schema", {})
                            response_schemas[code] = self._resolve_schema(schema)

                    endpoints.append(
                        {
                            "path": path,
                            "method": method.upper(),
                            "operation_id": operation_id,
                            "summary": summary,
                            "description": description,
                            "responses": response_schemas,
                        }
                    )
        return endpoints


class ValidationResult:
    """Result of contract validation"""

    def __init__(
        self,
        success: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        schema_path: str = "",
    ):
        self.success = success
        self.errors = errors or []
        self.warnings = warnings or []
        self.schema_path = schema_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings,
            "schema_path": self.schema_path,
        }

    def __repr__(self):
        status = "PASSED" if self.success else "FAILED"
        return f"ValidationResult({status}, errors={len(self.errors)}, warnings={len(self.warnings)})"


def create_contract_validator_from_file(spec_path: str) -> ContractValidator:
    """
    Create ContractValidator from OpenAPI YAML file

    Args:
        spec_path: Path to OpenAPI specification file

    Returns:
        ContractValidator instance
    """
    import yaml

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    return ContractValidator(spec)


def create_validator_from_dict(spec_dict: Dict[str, Any]) -> ContractValidator:
    """
    Create ContractValidator from parsed OpenAPI dictionary

    Args:
        spec_dict: Parsed OpenAPI specification

    Returns:
        ContractValidator instance
    """
    return ContractValidator(spec_dict)
