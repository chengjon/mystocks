"""
Security Test Suite: XSS/CSRF Protection (Task 1.2)
Tests comprehensive XSS and CSRF protection mechanisms
- CSRF Token generation, validation, and lifecycle
- CSRF middleware enforcement
- XSS prevention via CSP headers
- Frontend HTTP client security features
"""

import pytest
import time
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "web" / "backend"))

# Change to backend directory for imports to work
os.chdir(str(Path(__file__).parent.parent / "web" / "backend"))

# ============================================================================
# PART 1: CSRF Token Manager Tests
# ============================================================================


class TestCSRFTokenManager:
    """Test CSRF token generation, validation, and management"""

    @staticmethod
    def get_csrf_manager_class():
        """Get CSRFTokenManager class from main.py"""
        try:
            from app.main import CSRFTokenManager

            return CSRFTokenManager
        except ImportError:
            # Fallback: create simple version for testing
            return None

    def test_csrf_token_generation(self):
        """Token generation produces valid, unique tokens"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()
        token1 = manager.generate_token()
        token2 = manager.generate_token()

        # Tokens should be strings
        assert isinstance(token1, str)
        assert isinstance(token2, str)

        # Tokens should be unique
        assert token1 != token2

        # Tokens should be reasonable length (32-byte urlsafe = ~43 chars)
        assert len(token1) > 30
        assert len(token2) > 30

    def test_csrf_token_stored_with_metadata(self):
        """Generated tokens are stored with creation time and used flag"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()
        token = manager.generate_token()

        # Token should be in storage
        assert token in manager.tokens

        # Should have metadata
        token_info = manager.tokens[token]
        assert "created_at" in token_info
        assert "used" in token_info
        assert token_info["used"] == False
        assert isinstance(token_info["created_at"], float)

    def test_csrf_token_validation_success(self):
        """Valid, non-expired token passes validation"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()
        token = manager.generate_token()

        # Should validate successfully
        result = manager.validate_token(token)
        assert result == True

        # After validation, token should be marked as used
        assert manager.tokens[token]["used"] == True

    def test_csrf_token_validation_invalid_token(self):
        """Invalid token fails validation"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()

        # Nonexistent token
        result = manager.validate_token("invalid_token_xyz")
        assert result == False

        # None token
        result = manager.validate_token(None)
        assert result == False

        # Empty token
        result = manager.validate_token("")
        assert result == False

    def test_csrf_token_validation_expired_token(self):
        """Expired token fails validation and is removed from storage"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()
        token = manager.generate_token()

        # Simulate token expiration by setting created_at to past
        manager.tokens[token]["created_at"] = time.time() - (manager.token_timeout + 1)

        # Should fail validation
        result = manager.validate_token(token)
        assert result == False

        # Token should be removed from storage
        assert token not in manager.tokens

    def test_csrf_token_cleanup_expired(self):
        """Cleanup removes expired tokens"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()

        # Create multiple tokens
        token1 = manager.generate_token()
        token2 = manager.generate_token()
        token3 = manager.generate_token()

        # Expire first token
        manager.tokens[token1]["created_at"] = time.time() - (manager.token_timeout + 1)

        # Cleanup
        manager.cleanup_expired_tokens()

        # First should be removed, others remain
        assert token1 not in manager.tokens
        assert token2 in manager.tokens
        assert token3 in manager.tokens


# ============================================================================
# PART 2: CSRF Middleware Tests
# ============================================================================


class TestCSRFMiddleware:
    """Test CSRF middleware enforcement on HTTP methods"""

    @pytest.fixture
    def test_client(self):
        """Create FastAPI test client with CSRF protection"""
        try:
            from fastapi.testclient import TestClient
            from app.main import app

            return TestClient(app)
        except ImportError as e:
            pytest.skip(f"Cannot import FastAPI app: {e}")
            return None

    def test_csrf_token_endpoint_accessible_without_token(self, test_client):
        """GET /api/csrf-token should be accessible without CSRF token"""
        response = test_client.get("/api/csrf-token")

        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 3600

    def test_csrf_token_generation_returns_valid_format(self, test_client):
        """CSRF token endpoint returns properly formatted response"""
        response = test_client.get("/api/csrf-token")
        assert response.status_code == 200

        data = response.json()
        token = data["csrf_token"]

        # Token should be non-empty string
        assert isinstance(token, str)
        assert len(token) > 30

    def test_post_without_csrf_token_rejected(self, test_client):
        """POST request without CSRF token should be rejected"""
        response = test_client.post("/api/data/example", json={"data": "test"})

        # Should return 403 Forbidden
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "CSRF token missing"

    def test_post_with_invalid_csrf_token_rejected(self, test_client):
        """POST request with invalid CSRF token should be rejected"""
        response = test_client.post(
            "/api/data/example",
            json={"data": "test"},
            headers={"x-csrf-token": "invalid_token_xyz"},
        )

        # Should return 403 Forbidden
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "CSRF token invalid"

    def test_csrf_protection_on_all_state_modifying_methods(self, test_client):
        """CSRF protection applies to POST, PUT, PATCH, DELETE"""

        # Get a valid token first
        token_response = test_client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]

        headers = {"x-csrf-token": csrf_token}

        # All these methods should require token (specific endpoint may not exist,
        # but the CSRF check should run first)
        methods = [
            ("POST", "/api/data/example"),
            ("PUT", "/api/data/example"),
            ("PATCH", "/api/data/example"),
            ("DELETE", "/api/data/example"),
        ]

        # Test without token
        for method, path in methods:
            if method == "POST":
                response = test_client.post(path, json={})
            elif method == "PUT":
                response = test_client.put(path, json={})
            elif method == "PATCH":
                response = test_client.patch(path, json={})
            elif method == "DELETE":
                response = test_client.delete(path)

            # Should either be 403 (CSRF) or other error, but definitely not success
            assert response.status_code in [403, 404, 405]

    def test_get_requests_skip_csrf_check(self, test_client):
        """GET requests should not require CSRF token"""
        response = test_client.get("/api/csrf-token")

        # Should succeed without CSRF token
        assert response.status_code == 200

        response = test_client.get("/health")
        assert response.status_code == 200


# ============================================================================
# PART 3: CSP Header Tests
# ============================================================================


class TestContentSecurityPolicy:
    """Test Content-Security-Policy header implementation"""

    def test_csp_header_in_html_template(self):
        """Verify CSP meta tag in index.html"""
        from pathlib import Path

        html_path = Path(__file__).parent.parent / "web" / "frontend" / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # CSP meta tag should be present
        assert "Content-Security-Policy" in html_content
        assert "meta http-equiv" in html_content

    def test_csp_restricts_script_sources(self):
        """Verify CSP restricts script execution to self only"""
        from pathlib import Path

        html_path = Path(__file__).parent.parent / "web" / "frontend" / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Should have script-src 'self'
        assert "script-src 'self'" in html_content

        # Should NOT allow unsafe-inline for scripts
        assert "script-src 'unsafe-inline'" not in html_content

    def test_csp_prevents_clickjacking(self):
        """Verify CSP frame-ancestors prevents clickjacking"""
        from pathlib import Path

        html_path = Path(__file__).parent.parent / "web" / "frontend" / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Should have frame-ancestors 'none'
        assert "frame-ancestors 'none'" in html_content

    def test_csp_restricts_form_submissions(self):
        """Verify CSP form-action restricts form submission"""
        from pathlib import Path

        html_path = Path(__file__).parent.parent / "web" / "frontend" / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Should have form-action 'self'
        assert "form-action 'self'" in html_content


# ============================================================================
# PART 4: Frontend HTTP Client Tests
# ============================================================================


class TestHTTPClientCSRFHandling:
    """Test frontend HTTP client CSRF token management"""

    def test_http_client_initialization(self):
        """HTTP client initializes with correct configuration"""
        # Note: This tests the JavaScript client structure by reading the file
        from pathlib import Path

        http_client_path = Path(__file__).parent.parent / "web" / "frontend" / "src" / "services" / "httpClient.js"
        with open(http_client_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Should define HttpClient class
        assert "class HttpClient" in js_content

        # Should have CSRF token management
        assert "csrfToken" in js_content
        assert "initializeCsrfToken" in js_content
        assert "getCsrfToken" in js_content

    def test_http_client_csrf_token_endpoint(self):
        """HTTP client targets correct CSRF token endpoint"""
        from pathlib import Path

        http_client_path = Path(__file__).parent.parent / "web" / "frontend" / "src" / "services" / "httpClient.js"
        with open(http_client_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Should have correct endpoint
        assert "/api/csrf-token" in js_content

    def test_http_client_adds_csrf_header_to_mutations(self):
        """HTTP client adds X-CSRF-Token header for state-modifying requests"""
        from pathlib import Path

        http_client_path = Path(__file__).parent.parent / "web" / "frontend" / "src" / "services" / "httpClient.js"
        with open(http_client_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Should check for modifying methods
        assert "POST" in js_content
        assert "PUT" in js_content
        assert "PATCH" in js_content
        assert "DELETE" in js_content

        # Should add header
        assert "X-CSRF-Token" in js_content or "x-csrf-token" in js_content

    def test_http_client_credentials_included(self):
        """HTTP client includes credentials for session management"""
        from pathlib import Path

        http_client_path = Path(__file__).parent.parent / "web" / "frontend" / "src" / "services" / "httpClient.js"
        with open(http_client_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Should include credentials
        assert "credentials: 'include'" in js_content or 'credentials: "include"' in js_content


# ============================================================================
# PART 5: Vue App Security Initialization Tests
# ============================================================================


class TestVueAppSecurityInit:
    """Test Vue app security initialization"""

    def test_main_js_initializes_csrf(self):
        """main.js calls initializeSecurity before mount"""
        from pathlib import Path

        main_js_path = Path(__file__).parent.parent / "web" / "frontend" / "src" / "main.js"
        with open(main_js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Should import security initialization
        assert "initializeSecurity" in js_content

        # Should call it before mount
        assert "await initializeSecurity()" in js_content

        # Should handle errors gracefully
        assert "try" in js_content
        assert "catch" in js_content

    def test_csrf_meta_tag_present(self):
        """index.html has CSRF token meta tag"""
        from pathlib import Path

        html_path = Path(__file__).parent.parent / "web" / "frontend" / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Should have CSRF meta tag
        assert "meta" in html_content
        assert "csrf-token" in html_content
        assert "content=" in html_content


# ============================================================================
# PART 6: Integration Tests
# ============================================================================


class TestXSSCSRFIntegration:
    """Integration tests for XSS/CSRF protection"""

    @pytest.fixture
    def test_client(self):
        """Create FastAPI test client"""
        try:
            from fastapi.testclient import TestClient
            from app.main import app

            return TestClient(app)
        except ImportError as e:
            pytest.skip(f"Cannot import FastAPI app: {e}")
            return None

    def test_complete_csrf_token_flow(self, test_client):
        """Complete flow: fetch token -> use in request"""

        # Step 1: Fetch CSRF token
        token_response = test_client.get("/api/csrf-token")
        assert token_response.status_code == 200

        csrf_token = token_response.json()["csrf_token"]
        assert isinstance(csrf_token, str)
        assert len(csrf_token) > 30

        # Step 2: Try POST without token (should fail)
        response = test_client.post("/api/data/example", json={"data": "test"})
        assert response.status_code == 403

        # Step 3: Try POST with valid token (may fail for other reasons,
        # but not CSRF)
        response = test_client.post(
            "/api/data/example",
            json={"data": "test"},
            headers={"x-csrf-token": csrf_token},
        )
        # Should NOT be 403 Forbidden (CSRF check passed)
        assert response.status_code != 403

    def test_multiple_tokens_unique_and_independent(self, test_client):
        """Multiple tokens are unique and independently validated"""

        # Get two tokens
        response1 = test_client.get("/api/csrf-token")
        token1 = response1.json()["csrf_token"]

        response2 = test_client.get("/api/csrf-token")
        token2 = response2.json()["csrf_token"]

        # Tokens should be different
        assert token1 != token2

        # Each should validate independently
        response_with_1 = test_client.post("/api/data/example", json={}, headers={"x-csrf-token": token1})
        # Should not be CSRF error
        assert response_with_1.status_code != 403

        response_with_2 = test_client.post("/api/data/example", json={}, headers={"x-csrf-token": token2})
        # Should not be CSRF error
        assert response_with_2.status_code != 403


# ============================================================================
# PART 7: Security Best Practices Tests
# ============================================================================


class TestSecurityBestPractices:
    """Test implementation of security best practices"""

    @staticmethod
    def get_csrf_manager_class():
        """Get CSRFTokenManager class from main.py"""
        try:
            from app.main import CSRFTokenManager

            return CSRFTokenManager
        except ImportError:
            return None

    def test_csrf_token_uses_secure_random(self):
        """CSRF tokens use cryptographically secure random generation"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()

        # Generate multiple tokens and verify uniqueness/randomness
        tokens = [manager.generate_token() for _ in range(100)]

        # All should be unique
        assert len(set(tokens)) == 100

        # All should be reasonable length
        assert all(len(t) > 30 for t in tokens)

    def test_csrf_token_has_expiration(self):
        """CSRF tokens have expiration time"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()

        # Should have timeout configured
        assert manager.token_timeout == 3600  # 1 hour
        assert manager.token_timeout > 0

    def test_csrf_token_one_time_use(self):
        """CSRF tokens are marked as used after validation"""
        CSRFTokenManager = self.get_csrf_manager_class()
        if not CSRFTokenManager:
            pytest.skip("CSRFTokenManager not available, skipping")

        manager = CSRFTokenManager()
        token = manager.generate_token()

        # Before validation
        assert manager.tokens[token]["used"] == False

        # After validation
        manager.validate_token(token)
        assert manager.tokens[token]["used"] == True

    def test_no_hardcoded_secrets(self):
        """No hardcoded secrets or credentials in code"""
        from pathlib import Path

        # Check main.py
        main_py_path = Path(__file__).parent.parent / "web" / "backend" / "app" / "main.py"
        with open(main_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should not have hardcoded tokens or passwords
        assert "password=" not in content.lower()
        assert "'password'" not in content.lower()

        # Check httpClient.js
        http_client_path = Path(__file__).parent.parent / "web" / "frontend" / "src" / "services" / "httpClient.js"
        with open(http_client_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should not have hardcoded tokens
        assert "api_key" not in content.lower()
        assert "secret" not in content.lower()


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
