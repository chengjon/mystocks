"""
OpenAPI Specification Validator

Validates OpenAPI/Swagger specifications and extracts test cases.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HTTPMethod(str, Enum):
    """HTTP methods supported by API"""

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"


@dataclass
class Parameter:
    """API Parameter definition"""

    name: str
    in_: str  # path, query, header, body
    required: bool = False
    schema: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    type: str = "string"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "in": self.in_,
            "required": self.required,
            "schema": self.schema,
            "description": self.description,
            "type": self.type,
        }


@dataclass
class APIEndpoint:
    """API Endpoint definition from OpenAPI spec"""

    path: str
    method: HTTPMethod
    summary: str = ""
    description: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[Dict] = None
    responses: Dict[int, Dict] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    security: List[Dict] = field(default_factory=list)

    def get_signature(self) -> str:
        """Get endpoint signature for comparison"""
        return f"{self.method.value.upper()} {self.path}"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "path": self.path,
            "method": self.method.value,
            "summary": self.summary,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "request_body": self.request_body,
            "responses": self.responses,
            "tags": self.tags,
            "security": self.security,
        }


class SpecificationValidator:
    """
    Validates OpenAPI specification and extracts test cases.

    Task 12.1 Implementation: Specification validation and test case generation
    """

    def __init__(self, spec_path: Optional[str] = None):
        """
        Initialize validator

        Args:
            spec_path: Path to OpenAPI spec file (JSON or YAML)
        """
        self.spec_path = spec_path
        self.spec: Dict[str, Any] = {}
        self.endpoints: List[APIEndpoint] = []
        self.version = ""
        self.title = ""
        self.base_url = ""
        self.security_schemes: Dict = {}

        if spec_path:
            self.load_specification(spec_path)

    def load_specification(self, spec_path: str) -> Dict[str, Any]:
        """
        Load OpenAPI specification from file

        Args:
            spec_path: Path to spec file (.json or .yaml)

        Returns:
            Loaded specification dictionary
        """
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        try:
            if spec_path.endswith(".json"):
                with open(spec_path, "r", encoding="utf-8") as f:
                    self.spec = json.load(f)
            elif spec_path.endswith((".yaml", ".yml")):
                with open(spec_path, "r", encoding="utf-8") as f:
                    self.spec = yaml.safe_load(f)
            else:
                raise ValueError("Specification must be .json or .yaml file")

            logger.info(f"✅ Loaded specification from {spec_path}")
            self._validate_spec_structure()
            self._extract_metadata()
            self._parse_endpoints()

            return self.spec

        except Exception as e:
            logger.error(f"❌ Failed to load specification: {e}")
            raise

    def _validate_spec_structure(self) -> bool:
        """
        Validate OpenAPI specification structure

        Returns:
            True if valid
        """
        if not self.spec:
            raise ValueError("Specification is empty")

        # Check OpenAPI version
        openapi_version = self.spec.get("openapi") or self.spec.get("swagger")
        if not openapi_version:
            raise ValueError("Missing 'openapi' or 'swagger' field")

        # Check required fields
        required_fields = ["info", "paths"]
        for field in required_fields:
            if field not in self.spec:
                raise ValueError(f"Missing required field: {field}")

        logger.info(f"✅ Specification structure is valid (OpenAPI {openapi_version})")
        return True

    def _extract_metadata(self) -> None:
        """Extract metadata from specification"""
        info = self.spec.get("info", {})
        self.title = info.get("title", "Unknown API")
        self.version = info.get("version", "unknown")

        # Extract base URL
        servers = self.spec.get("servers", [])
        if servers and isinstance(servers, list) and len(servers) > 0:
            self.base_url = servers[0].get("url", "")

        # Extract security schemes
        self.security_schemes = self.spec.get("components", {}).get(
            "securitySchemes", {}
        )

        logger.info(f"📋 API Title: {self.title} v{self.version}")
        logger.info(f"🔗 Base URL: {self.base_url or 'Not specified'}")
        logger.info(
            f"🔐 Security Schemes: {list(self.security_schemes.keys()) or 'None'}"
        )

    def _parse_endpoints(self) -> None:
        """Parse endpoints from specification"""
        self.endpoints = []
        paths = self.spec.get("paths", {})

        for path, methods_spec in paths.items():
            for method_name, method_spec in methods_spec.items():
                if method_name.lower() not in [m.value for m in HTTPMethod]:
                    continue

                try:
                    endpoint = self._parse_endpoint(path, method_name, method_spec)
                    self.endpoints.append(endpoint)
                except Exception as e:
                    logger.warning(
                        f"⚠️  Failed to parse {method_name.upper()} {path}: {e}"
                    )

        logger.info(f"✅ Parsed {len(self.endpoints)} endpoints from specification")

    def _parse_endpoint(self, path: str, method: str, spec: Dict) -> APIEndpoint:
        """
        Parse individual endpoint specification

        Args:
            path: URL path
            method: HTTP method
            spec: Endpoint specification

        Returns:
            APIEndpoint object
        """
        # Parse parameters
        parameters = []
        for param_spec in spec.get("parameters", []):
            param = Parameter(
                name=param_spec.get("name", ""),
                in_=param_spec.get("in", "query"),
                required=param_spec.get("required", False),
                description=param_spec.get("description", ""),
                type=param_spec.get("schema", {}).get("type", "string"),
                schema=param_spec.get("schema", {}),
            )
            parameters.append(param)

        # Parse request body
        request_body = None
        if "requestBody" in spec:
            request_body = spec["requestBody"]

        # Parse responses
        responses = spec.get("responses", {})

        # Create endpoint
        endpoint = APIEndpoint(
            path=path,
            method=HTTPMethod[method.upper()],
            summary=spec.get("summary", ""),
            description=spec.get("description", ""),
            parameters=parameters,
            request_body=request_body,
            responses={int(k): v for k, v in responses.items() if k.isdigit()},
            tags=spec.get("tags", []),
            security=spec.get("security", []),
        )

        return endpoint

    def get_all_endpoints(self) -> List[APIEndpoint]:
        """Get all parsed endpoints"""
        return self.endpoints

    def get_endpoints_by_tag(self, tag: str) -> List[APIEndpoint]:
        """Get endpoints by tag"""
        return [ep for ep in self.endpoints if tag in ep.tags]

    def get_endpoint(self, method: str, path: str) -> Optional[APIEndpoint]:
        """
        Get specific endpoint

        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path

        Returns:
            APIEndpoint or None
        """
        method = method.upper()
        for ep in self.endpoints:
            if ep.method.value.upper() == method and ep.path == path:
                return ep
        return None

    def get_summary(self) -> Dict:
        """Get specification summary"""
        return {
            "title": self.title,
            "version": self.version,
            "base_url": self.base_url,
            "total_endpoints": len(self.endpoints),
            "endpoints_by_tag": self._count_endpoints_by_tag(),
            "security_schemes": list(self.security_schemes.keys()),
            "methods": self._count_methods(),
        }

    def _count_endpoints_by_tag(self) -> Dict[str, int]:
        """Count endpoints by tag"""
        tag_counts = {}
        for endpoint in self.endpoints:
            for tag in endpoint.tags or ["Untagged"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts

    def _count_methods(self) -> Dict[str, int]:
        """Count endpoints by HTTP method"""
        method_counts = {}
        for endpoint in self.endpoints:
            method = endpoint.method.value.upper()
            method_counts[method] = method_counts.get(method, 0) + 1
        return method_counts

    def export_endpoints_json(self, output_path: str) -> None:
        """Export parsed endpoints to JSON"""
        endpoints_data = [ep.to_dict() for ep in self.endpoints]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(endpoints_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Exported {len(endpoints_data)} endpoints to {output_path}")
