"""
Request Router - API versioning and request routing

Handles routing with version support, path normalization,
and intelligent request routing based on patterns.

Task 11: API Gateway and Request Routing
Author: Claude Code
Date: 2025-11-07
"""

from dataclasses import dataclass
from typing import Dict, Optional, List, Callable, Any
from enum import Enum
import re
import structlog

logger = structlog.get_logger()


class HTTPMethod(str, Enum):
    """HTTP Methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RouteConfig:
    """Route configuration"""

    path: str  # Route path pattern (supports {param} placeholders)
    methods: List[str]  # Allowed HTTP methods
    handler: Optional[Callable] = None  # Handler function
    description: str = ""
    version: str = "v1"  # API version
    rate_limit_tokens: int = 1  # Tokens consumed per request
    timeout_seconds: int = 30
    require_auth: bool = False


class RequestRouter:
    """Router for API requests with versioning support"""

    def __init__(self, base_path: str = "/api"):
        """Initialize request router

        Args:
            base_path: Base path for all routes (default: /api)
        """
        self.base_path = base_path
        self.routes: Dict[str, List[RouteConfig]] = {}
        self.route_cache: Dict[str, RouteConfig] = {}
        logger.info("✅ Request Router initialized", base_path=base_path)

    def register_route(self, config: RouteConfig) -> None:
        """Register a route

        Args:
            config: Route configuration
        """
        # Normalize path
        normalized_path = self._normalize_path(config.path)
        route_key = f"{config.version}:{normalized_path}"

        if route_key not in self.routes:
            self.routes[route_key] = []

        self.routes[route_key].append(config)

        # Clear cache
        self.route_cache.clear()

        logger.info(
            "✅ Route registered",
            path=normalized_path,
            version=config.version,
            methods=config.methods,
        )

    def register_routes(self, configs: List[RouteConfig]) -> None:
        """Register multiple routes

        Args:
            configs: List of route configurations
        """
        for config in configs:
            self.register_route(config)

    def find_route(
        self, path: str, method: str, version: str = "v1"
    ) -> Optional[RouteConfig]:
        """Find matching route for request

        Args:
            path: Request path
            method: HTTP method
            version: API version

        Returns:
            Route configuration or None if not found
        """
        normalized_path = self._normalize_path(path)
        route_key = f"{version}:{normalized_path}"

        # Check exact match first
        if route_key in self.routes:
            for route in self.routes[route_key]:
                if method.upper() in [m.upper() for m in route.methods]:
                    return route

        # Check pattern matches
        for key, route_list in self.routes.items():
            if key.startswith(f"{version}:"):
                pattern = key.split(":", 1)[1]
                if self._match_pattern(pattern, normalized_path):
                    for route in route_list:
                        if method.upper() in [m.upper() for m in route.methods]:
                            return route

        return None

    def match_pattern(self, pattern: str, path: str) -> bool:
        """Check if path matches route pattern

        Args:
            pattern: Route pattern (e.g., /api/v1/users/{id})
            path: Request path

        Returns:
            True if path matches pattern
        """
        return self._match_pattern(pattern, path)

    def extract_path_params(self, pattern: str, path: str) -> Dict[str, str]:
        """Extract path parameters from URL

        Args:
            pattern: Route pattern
            path: Request path

        Returns:
            Dictionary of extracted parameters
        """
        # Convert pattern to regex
        regex_pattern = self._pattern_to_regex(pattern)
        match = re.match(regex_pattern, path)

        if not match:
            return {}

        return match.groupdict()

    def normalize_version(self, version: Optional[str]) -> str:
        """Normalize version string

        Args:
            version: Version string (e.g., "1", "v1", "V1")

        Returns:
            Normalized version string (e.g., "v1")
        """
        if not version:
            return "v1"

        version_str = str(version).lower()
        if not version_str.startswith("v"):
            version_str = f"v{version_str}"

        return version_str

    def get_routes_summary(self) -> Dict[str, Any]:
        """Get summary of registered routes

        Returns:
            Summary dictionary
        """
        summary = {
            "total_routes": sum(len(routes) for routes in self.routes.values()),
            "versions": set(),
            "by_version": {},
        }

        for key, routes in self.routes.items():
            version, path = key.split(":", 1)
            summary["versions"].add(version)

            if version not in summary["by_version"]:
                summary["by_version"][version] = []

            for route in routes:
                summary["by_version"][version].append(
                    {
                        "path": path,
                        "methods": route.methods,
                        "description": route.description,
                    }
                )

        summary["versions"] = sorted(list(summary["versions"]))
        return summary

    def _normalize_path(self, path: str) -> str:
        """Normalize path string

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

    def _match_pattern(self, pattern: str, path: str) -> bool:
        """Check if path matches pattern

        Args:
            pattern: Route pattern
            path: Request path

        Returns:
            True if path matches
        """
        regex = self._pattern_to_regex(pattern)
        return bool(re.match(regex, path))

    def _pattern_to_regex(self, pattern: str) -> str:
        """Convert route pattern to regex

        Args:
            pattern: Route pattern (e.g., /users/{id}/posts/{post_id})

        Returns:
            Regex pattern string
        """
        # Escape special characters except for placeholders
        regex = re.escape(pattern)

        # Replace escaped placeholders with regex groups
        # {name} -> (?P<name>[^/]+)
        regex = re.sub(r"\\{(\w+)\\}", r"(?P<\1>[^/]+)", regex)

        # Add anchors
        regex = f"^{regex}$"

        return regex


class RequestRouterManager:
    """Manager for multiple API routers with version support"""

    def __init__(self, base_path: str = "/api"):
        """Initialize router manager

        Args:
            base_path: Base path for API
        """
        self.base_path = base_path
        self.routers: Dict[str, RequestRouter] = {}
        logger.info("✅ Request Router Manager initialized", base_path=base_path)

    def get_router(self, version: str = "v1") -> RequestRouter:
        """Get or create router for version

        Args:
            version: API version

        Returns:
            Request router
        """
        if version not in self.routers:
            self.routers[version] = RequestRouter(self.base_path)

        return self.routers[version]

    def register_route(self, config: RouteConfig) -> None:
        """Register route across all routers

        Args:
            config: Route configuration
        """
        router = self.get_router(config.version)
        router.register_route(config)

    def find_route(
        self, path: str, method: str, version: str = "v1"
    ) -> Optional[RouteConfig]:
        """Find route across routers

        Args:
            path: Request path
            method: HTTP method
            version: API version

        Returns:
            Route configuration or None
        """
        router = self.routers.get(version)
        if router is None:
            return None

        return router.find_route(path, method, version)

    def get_all_routes(self) -> Dict[str, Dict[str, Any]]:
        """Get all routes organized by version

        Returns:
            Dictionary of routes by version
        """
        return {
            version: router.get_routes_summary()
            for version, router in self.routers.items()
        }
