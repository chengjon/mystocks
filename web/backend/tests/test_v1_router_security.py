from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api.v1.router import api_v1_router
from app.main import app


EXPECTED_RUNTIME_AUTH_PATHS = {
    "/api/v1/auth/csrf/token",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
    "/api/v1/auth/refresh",
    "/api/v1/auth/register",
    "/api/v1/auth/reset-password/confirm",
    "/api/v1/auth/reset-password/request",
    "/api/v1/auth/users",
}


def test_v1_router_excludes_admin_auth_routes() -> None:
    auth_route_modules = {
        route.endpoint.__module__
        for route in api_v1_router.routes
        if route.path.startswith("/api/v1/auth")
    }

    assert auth_route_modules == set()


def test_runtime_v1_auth_routes_are_served_by_canonical_auth_router() -> None:
    runtime_auth_routes = {
        route.path: route.endpoint.__module__
        for route in app.routes
        if getattr(route, "path", "").startswith("/api/v1/auth")
    }

    assert set(runtime_auth_routes) == EXPECTED_RUNTIME_AUTH_PATHS
    assert set(runtime_auth_routes.values()) == {"app.api.auth"}
