from app.api.v1.router import api_v1_router


def test_v1_router_excludes_admin_auth_routes():
    insecure_route_modules = {
        route.endpoint.__module__
        for route in api_v1_router.routes
        if route.path.startswith("/auth")
    }

    assert "app.api.v1.admin.auth" not in insecure_route_modules
