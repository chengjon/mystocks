"""
OpenAPI Specification Generator

Generates OpenAPI specification from FastAPI application routes.
Enables Code-to-DB: Auto-generate OpenAPI spec from code routes.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.routing import Route

logger = logging.getLogger(__name__)


@dataclass
class EndpointInfo:
    """Information extracted from a FastAPI endpoint"""

    path: str
    method: str
    name: str
    summary: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    request_model: Optional[Type[BaseModel]] = None
    response_model: Optional[Type[BaseModel]] = None
    path_params: List[Dict[str, Any]] = field(default_factory=list)
    query_params: List[Dict[str, Any]] = field(default_factory=list)
    response_codes: Dict[str, Dict] = field(default_factory=dict)


class OpenAPIGenerator:
    """
    Generates OpenAPI specification from FastAPI application.

    Performs Code-to-DB: Extracts API structure from code and generates OpenAPI spec.
    """

    def __init__(self, title: str = "MyStocks API", version: str = "1.0.0"):
        """
        Initialize OpenAPI generator.

        Args:
            title: API title
            version: API version
        """
        self.title = title
        self.version = version
        self.endpoints: List[EndpointInfo] = []

    def scan_app(self, app: FastAPI) -> None:
        """
        Scan FastAPI application and extract endpoint information.

        Args:
            app: FastAPI application instance
        """
        self.endpoints = []

        for route in app.routes:
            if isinstance(route, Route):
                self._extract_route(route, app)

    def _extract_route(self, route: Route, app: FastAPI) -> None:
        """Extract information from a single route"""
        path = route.path_format
        methods = route.methods

        for method in methods:
            endpoint = route.endpoint
            name = endpoint.__name__

            # Get route info from decorators
            route_info = getattr(endpoint, "__route_info__", {})

            info = EndpointInfo(
                path=path,
                method=method,
                name=name,
                summary=route_info.get("summary", ""),
                description=route_info.get("description", ""),
                tags=route_info.get("tags", []),
                deprecated=route_info.get("deprecated", False),
            )

            # Extract parameters from path format
            info.path_params = self._extract_path_params(path)

            # Try to get request/response models
            info.request_model = self._get_request_model(endpoint)
            info.response_model = self._get_response_model(endpoint)

            # Set default response codes
            info.response_codes = {
                "200": {"description": "Successful response"},
                "400": {"description": "Bad request"},
                "401": {"description": "Unauthorized"},
                "404": {"description": "Not found"},
                "500": {"description": "Internal server error"},
            }

            self.endpoints.append(info)
            logger.debug("Extracted endpoint: %(method)s %(path)s"")

    def _extract_path_params(self, path: str) -> List[Dict[str, Any]]:
        """Extract path parameters from path format"""
        params = []
        import re

        matches = re.findall(r"\{(\w+)(:[^}]+)?\}", path)
        for match in matches:
            param_name = match[0]
            param_type = match[1].lstrip(":") if match[1] else "string"

            type_map = {
                "str": "string",
                "int": "integer",
                "float": "number",
                "bool": "boolean",
            }

            params.append(
                {
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": type_map.get(param_type, "string")},
                    "description": f"Path parameter: {param_name}",
                }
            )

        return params

    def _get_request_model(self, endpoint) -> Optional[Type[BaseModel]]:
        """Get request model from endpoint"""
        # Check for Depends injection
        if hasattr(endpoint, "__dependencies__"):
            for dep in endpoint.__dependencies__:
                if hasattr(dep, "dependency"):
                    model = getattr(dep.dependency, "__pydantic_model__", None)
                    if model:
                        return model

        # Check for body parameter in signature
        getattr(endpoint, "__signature__", {}).parameters if hasattr(endpoint, "__signature__") else {}

        return None

    def _get_response_model(self, endpoint) -> Optional[Type[BaseModel]]:
        """Get response model from endpoint"""
        # Check for response_model attribute
        if hasattr(endpoint, "__annotations__"):
            return_type = endpoint.__annotations__.get("return")
            if return_type and hasattr(return_type, "__pydantic_model__"):
                return return_type.__pydantic_model__

        return None

    def generate_spec(self) -> Dict[str, Any]:
        """
        Generate complete OpenAPI specification.

        Returns:
            OpenAPI specification dictionary
        """
        spec = {
            "openapi": "3.1.0",
            "info": {"title": self.title, "version": self.version, "description": self._generate_description()},
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
            },
            "tags": [],
        }

        # Generate paths
        for endpoint in self.endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}

            spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary or endpoint.name,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "deprecated": endpoint.deprecated,
                "parameters": endpoint.path_params + endpoint.query_params,
                "responses": endpoint.response_codes,
            }

            # Add request body for POST/PUT/PATCH
            if endpoint.method in ["POST", "PUT", "PATCH"] and endpoint.request_model:
                request_schema = self._model_to_schema(endpoint.request_model)
                spec["paths"][endpoint.path][endpoint.method.lower()].setdefault(
                    "requestBody", {"required": True, "content": {"application/json": {"schema": request_schema}}}
                )

            # Add response schema
            if endpoint.response_model:
                response_schema = self._model_to_schema(endpoint.response_model)
                if "200" in spec["paths"][endpoint.path][endpoint.method.lower()]["responses"]:
                    spec["paths"][endpoint.path][endpoint.method.lower()]["responses"]["200"]["content"] = {
                        "application/json": {"schema": response_schema}
                    }

        # Generate schemas
        for endpoint in self.endpoints:
            if endpoint.request_model:
                spec["components"]["schemas"][endpoint.request_model.__name__] = self._model_to_schema(
                    endpoint.request_model
                )
            if endpoint.response_model:
                spec["components"]["schemas"][endpoint.response_model.__name__] = self._model_to_schema(
                    endpoint.response_model
                )

        # Generate tags from endpoint tags
        all_tags = set()
        for endpoint in self.endpoints:
            all_tags.update(endpoint.tags)

        for tag in all_tags:
            spec["tags"].append({"name": tag, "description": f"Endpoints for {tag}"})

        return spec

    def _model_to_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Convert Pydantic model to OpenAPI schema"""
        schema = {"type": "object", "properties": {}, "required": []}

        for name, model_field in model.model_fields.items():
            field_info = model_field.annotation

            # Determine type
            type_str = self._python_type_to_openapi(field_info)

            prop_schema = {"type": type_str, "description": model_field.description or ""}

            if model_field.default is not None:
                prop_schema["default"] = model_field.default
            elif not model_field.is_required():
                pass  # Optional, no default

            schema["properties"][name] = prop_schema

            if field.is_required():
                schema["required"].append(name)

        return schema

    def _python_type_to_openapi(self, typ: Any) -> str:
        """Convert Python type to OpenAPI type string"""
        if typ is str:
            return "string"
        elif typ is int:
            return "integer"
        elif typ is float:
            return "number"
        elif typ is bool:
            return "boolean"
        elif hasattr(typ, "__origin__"):
            # Generic types like List[str], Optional[str]
            origin = typ.__origin__
            if origin is list:
                return "array"
            elif origin is dict:
                return "object"
        elif hasattr(typ, "__args__"):
            # Other generic types
            args = typ.__args__
            if len(args) == 2 and args[1] is type(None):
                # Optional
                return self._python_type_to_openapi(args[0])

        return "string"

    def _generate_description(self) -> str:
        """Generate API description"""
        return f"""
# {self.title}

Auto-generated from FastAPI application code.

## Endpoints

Total endpoints: {len(self.endpoints)}

### Methods
- GET: {sum(1 for e in self.endpoints if e.method == "GET")}
- POST: {sum(1 for e in self.endpoints if e.method == "POST")}
- PUT: {sum(1 for e in self.endpoints if e.method == "PUT")}
- DELETE: {sum(1 for e in self.endpoints if e.method == "DELETE")}
- PATCH: {sum(1 for e in self.endpoints if e.method == "PATCH")}
        """.strip()

    def save_spec(self, path: str, format: str = "yaml") -> None:
        """
        Save generated specification to file.

        Args:
            path: Output file path
            format: Output format ('yaml' or 'json')
        """
        spec = self.generate_spec()

        if format == "yaml":
            import yaml

            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(spec, f, allow_unicode=True, sort_keys=False)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(spec, f, ensure_ascii=False, indent=2)

        logger.info("Saved OpenAPI spec to %(path)s"")

    def get_sync_report(self) -> Dict[str, Any]:
        """
        Get report of what would be synced.

        Returns:
            Sync report dictionary
        """
        return {
            "total_endpoints": len(self.endpoints),
            "endpoints_by_method": {
                "GET": sum(1 for e in self.endpoints if e.method == "GET"),
                "POST": sum(1 for e in self.endpoints if e.method == "POST"),
                "PUT": sum(1 for e in self.endpoints if e.method == "PUT"),
                "DELETE": sum(1 for e in self.endpoints if e.method == "DELETE"),
                "PATCH": sum(1 for e in self.endpoints if e.method == "PATCH"),
            },
            "endpoints_by_path": self._group_by_path(),
        }

    def _group_by_path(self) -> Dict[str, List[str]]:
        """Group endpoints by path"""
        grouped = {}
        for endpoint in self.endpoints:
            if endpoint.path not in grouped:
                grouped[endpoint.path] = []
            grouped[endpoint.path].append(endpoint.method)
        return grouped


def generate_openapi_from_app(app: FastAPI, title: str = "MyStocks API", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Convenience function to generate OpenAPI spec from FastAPI app.

    Args:
        app: FastAPI application instance
        title: API title
        version: API version

    Returns:
        OpenAPI specification dictionary
    """
    generator = OpenAPIGenerator(title=title, version=version)
    generator.scan_app(app)
    return generator.generate_spec()
