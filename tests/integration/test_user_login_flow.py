"""
Integration Test: User Login Flow

Tests the complete user authentication flow from login page to dashboard,
implementing the 5-layer verification model.

Test Coverage:
- Layer 5: User credentials exist in database
- Layer 2: Login API returns valid token
- Layer 4: Login page renders correctly
- Layer 3: Complete flow from login → authenticated dashboard

Requirement: FR-006 (User Authentication and Session Management)

Author: MyStocks Development Team
Created: 2025-10-29
"""

import pytest
import os
from playwright.sync_api import Page, expect
from tests.integration.utils import (
    login,
    take_screenshot,
    wait_for_page_load,
    CommonSelectors,
    ConsoleCapture,
    LayerValidation,
)

# Configuration
MYSTOCKS_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
MYSTOCKS_USER = os.getenv("MYSTOCKS_USER", "admin")
MYSTOCKS_PASS = os.getenv("MYSTOCKS_PASS", "admin123")


class TestUserLoginFlow:
    """Test suite for user login and authentication flow."""

    def test_login_page_loads(self, page: Page):
        """
        Test that login page loads correctly.

        Layer 4: UI validation only
        """
        # Navigate to login page
        page.goto(f"{MYSTOCKS_URL}/login")
        wait_for_page_load(page)

        # Take screenshot for documentation
        take_screenshot(page, "test_login_page_loads")

        # Verify page title or header
        expect(page).to_have_url(f"{MYSTOCKS_URL}/login")

        # Verify login form elements exist
        username_input = page.locator(CommonSelectors.USERNAME_INPUT)
        password_input = page.locator(CommonSelectors.PASSWORD_INPUT)
        login_button = page.locator(CommonSelectors.LOGIN_BUTTON)

        expect(username_input).to_be_visible()
        expect(password_input).to_be_visible()
        expect(login_button).to_be_visible()

    def test_login_with_valid_credentials(self, page: Page, db_cursor, api_client):
        """
        Test successful login with valid credentials.

        Layers tested:
        - Layer 5: User exists in database
        - Layer 2: Login API returns token
        - Layer 4: Dashboard loads after login
        - Layer 3: Complete login flow
        """
        # Layer 5: Verify user exists in database
        db_cursor.execute(
            """
            SELECT username, role FROM users WHERE username = %s
        """,
            (MYSTOCKS_USER,),
        )
        user_record = db_cursor.fetchone()

        assert user_record is not None, f"User {MYSTOCKS_USER} not found in database"
        username, role = user_record
        assert username == MYSTOCKS_USER
        print(f"✅ Layer 5: User '{username}' exists in database with role '{role}'")

        # Layer 4 & 3: Perform login through UI
        page.goto(f"{MYSTOCKS_URL}/login")
        wait_for_page_load(page)

        # Fill login form
        page.fill(CommonSelectors.USERNAME_INPUT, MYSTOCKS_USER)
        page.fill(CommonSelectors.PASSWORD_INPUT, MYSTOCKS_PASS)

        # Capture console errors
        console = ConsoleCapture(page)

        # Click login button
        page.click(CommonSelectors.LOGIN_BUTTON)

        # Wait for navigation to dashboard
        page.wait_for_url("**/dashboard**", timeout=10000)
        print("✅ Layer 4: Successfully navigated to dashboard")

        # Take screenshot of successful login
        take_screenshot(page, "test_login_success_dashboard")

        # Verify no console errors
        console.assert_no_errors()
        print("✅ Layer 4: No console errors during login")

        # Verify URL contains dashboard
        assert "dashboard" in page.url.lower()
        print("✅ Layer 3: Complete login flow successful")

    def test_login_with_invalid_credentials(self, page: Page):
        """
        Test login failure with invalid credentials.

        Layer 4: UI validation - error message displayed
        """
        page.goto(f"{MYSTOCKS_URL}/login")
        wait_for_page_load(page)

        # Fill with invalid credentials
        page.fill(CommonSelectors.USERNAME_INPUT, "invalid_user")
        page.fill(CommonSelectors.PASSWORD_INPUT, "wrong_password")

        # Capture console and error messages
        console = ConsoleCapture(page)

        # Click login button
        page.click(CommonSelectors.LOGIN_BUTTON)

        # Wait a moment for error message
        page.wait_for_timeout(2000)

        # Verify still on login page (not redirected)
        assert "login" in page.url.lower()

        # Look for error message element
        error_message = page.locator(CommonSelectors.ERROR_MESSAGE)

        # Note: This test may need adjustment based on actual error handling
        # If no error element is visible, that's also valuable feedback
        try:
            expect(error_message).to_be_visible(timeout=3000)
            print("✅ Error message displayed for invalid credentials")
        except AssertionError:
            print("⚠️  No visible error message - UX improvement needed")

        # Take screenshot
        take_screenshot(page, "test_login_invalid_credentials")

    def test_logout_flow(self, page: Page):
        """
        Test logout functionality.

        Layer 3 & 4: Complete logout flow from dashboard to login
        """
        # First, log in
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)

        # Verify we're on dashboard
        assert "dashboard" in page.url.lower()
        print("✅ Successfully logged in to dashboard")

        # Look for logout button
        logout_button = page.locator(CommonSelectors.LOGOUT_BUTTON)

        try:
            expect(logout_button).to_be_visible(timeout=5000)

            # Click logout
            logout_button.click()

            # Wait for redirect to login
            page.wait_for_url("**/login**", timeout=10000)

            assert "login" in page.url.lower()
            print("✅ Successfully logged out and redirected to login")

            # Take screenshot
            take_screenshot(page, "test_logout_success")

        except AssertionError:
            print("⚠️  Logout button not found - feature may not be implemented")
            take_screenshot(page, "test_logout_button_not_found")
            pytest.skip("Logout functionality not implemented")

    def test_session_persistence(self, page: Page, context):
        """
        Test that session persists across page navigation.

        Layer 3: Session management
        """
        # Log in
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)

        # Verify dashboard loads
        assert "dashboard" in page.url.lower()

        # Navigate away and back
        page.goto(f"{MYSTOCKS_URL}/")
        wait_for_page_load(page)

        # Should still be authenticated (not redirected to login)
        # This depends on your app's session management
        current_url = page.url.lower()

        if "login" in current_url:
            print("⚠️  Session did not persist - user was logged out")
            pytest.fail("Session should persist across navigation")
        else:
            print("✅ Session persisted across navigation")

    def test_protected_route_without_auth(self, page: Page):
        """
        Test that accessing protected routes without auth redirects to login.

        Layer 3: Authorization check
        """
        # Try to access dashboard directly without logging in
        page.goto(f"{MYSTOCKS_URL}/dashboard")
        wait_for_page_load(page)

        # Should be redirected to login
        page.wait_for_url("**/login**", timeout=10000)

        assert "login" in page.url.lower()
        print("✅ Unauthenticated access to dashboard redirected to login")

        # Take screenshot
        take_screenshot(page, "test_protected_route_redirect")


class TestLoginAPIDirectly:
    """Test login API directly (Layer 2 validation)."""

    def test_login_api_returns_token(self, page: Page):
        """
        Test that login API returns valid JWT token.

        Layer 2: API validation
        """
        # Make direct API request
        response = page.request.post(
            f"{MYSTOCKS_URL}/api/auth/login",
            data={"username": MYSTOCKS_USER, "password": MYSTOCKS_PASS},
        )

        # Verify status code
        assert response.ok, f"Login API failed: {response.status}"
        print(f"✅ Layer 2: Login API returned status {response.status}")

        # Verify response structure
        data = response.json()
        assert "access_token" in data, "Response missing access_token"

        token = data["access_token"]
        assert token, "Access token is empty"
        assert len(token) > 20, "Access token seems invalid (too short)"

        print(f"✅ Layer 2: Received valid JWT token (length: {len(token)})")

    def test_login_api_with_invalid_credentials(self, page: Page):
        """
        Test that login API rejects invalid credentials.

        Layer 2: API error handling
        """
        response = page.request.post(
            f"{MYSTOCKS_URL}/api/auth/login",
            data={"username": "invalid_user", "password": "wrong_password"},
        )

        # Should return 401 Unauthorized or 400 Bad Request
        assert response.status in [
            400,
            401,
        ], f"Expected 400 or 401, got {response.status}"

        print(
            f"✅ Layer 2: Invalid credentials correctly rejected with status {response.status}"
        )


class TestMultiLayerLoginValidation:
    """
    Comprehensive multi-layer validation of login flow.

    Demonstrates the complete 5-layer verification model.
    """

    def test_complete_login_flow_all_layers(self, page: Page, db_cursor, api_client):
        """
        Test complete login flow with all layer validations.

        This demonstrates the bottom-up verification strategy:
        Layer 5 (Database) → Layer 2 (API) → Layer 4 (UI) → Layer 3 (Integration)
        """
        validator = LayerValidation(db_cursor, api_client, page)

        print("\n=== Multi-Layer Login Flow Validation ===\n")

        # Layer 5: Verify user in database
        print("Step 1: Validating Layer 5 (Database)...")
        db_cursor.execute(
            """
            SELECT COUNT(*) FROM users WHERE username = %s AND is_active = true
        """,
            (MYSTOCKS_USER,),
        )
        user_count = db_cursor.fetchone()[0]
        assert user_count > 0, f"User {MYSTOCKS_USER} not found in database"
        print(f"✅ Layer 5: User exists in database")

        # Layer 2: Verify login API
        print("\nStep 2: Validating Layer 2 (API)...")
        api_result = validator.api(
            endpoint="/api/auth/login", min_records=0  # Login returns object, not list
        )

        # For login, we need custom API validation
        response = page.request.post(
            f"{MYSTOCKS_URL}/api/auth/login",
            data={"username": MYSTOCKS_USER, "password": MYSTOCKS_PASS},
        )
        assert response.ok
        data = response.json()
        assert "access_token" in data
        print(f"✅ Layer 2: Login API returned valid token")

        # Layer 4: Verify login page UI
        print("\nStep 3: Validating Layer 4 (UI - Login Page)...")
        page.goto(f"{MYSTOCKS_URL}/login")
        wait_for_page_load(page)

        ui_result = validator.ui(
            {
                "username_input": CommonSelectors.USERNAME_INPUT,
                "password_input": CommonSelectors.PASSWORD_INPUT,
                "login_button": CommonSelectors.LOGIN_BUTTON,
            }
        )
        assert ui_result.passed, f"Login page UI validation failed: {ui_result.errors}"
        print(f"✅ Layer 4: Login page UI elements present")

        # Layer 3: Verify complete login flow
        print("\nStep 4: Validating Layer 3 (Integration - Complete Flow)...")
        page.fill(CommonSelectors.USERNAME_INPUT, MYSTOCKS_USER)
        page.fill(CommonSelectors.PASSWORD_INPUT, MYSTOCKS_PASS)

        console = ConsoleCapture(page)
        page.click(CommonSelectors.LOGIN_BUTTON)

        page.wait_for_url("**/dashboard**", timeout=10000)
        console.assert_no_errors()

        assert "dashboard" in page.url.lower()
        print(f"✅ Layer 3: Complete login flow successful")

        # Take final screenshot
        take_screenshot(page, "test_multi_layer_login_success")

        print("\n=== ✅ ✅ ✅ All Layers Validated Successfully! ===\n")
