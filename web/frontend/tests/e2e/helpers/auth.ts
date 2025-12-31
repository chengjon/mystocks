/**
 * Authentication Helper for E2E Tests
 *
 * Provides utilities for logging in and managing authentication state
 * in E2E tests. Supports both JWT token authentication and CSRF token handling.
 *
 * @see {@link https://playwright.dev/docs/api-testing} | API Testing with Playwright
 */

import { APIRequestContext, Page } from '@playwright/test';

/**
 * Configuration for authentication
 */
const AUTH_CONFIG = {
  /**
   * Base URL for API requests
   */
  baseURL: process.env.BASE_URL || 'http://localhost:8000',

  /**
   * Login endpoint path
   */
  loginPath: '/api/v1/auth/login',

  /**
   * CSRF token endpoint path
   */
  csrfPath: '/api/csrf-token',

  /**
   * Default test credentials
   */
  defaultCredentials: {
    username: 'admin',
    password: process.env.ADMIN_PASSWORD || 'admin123',
  },
};

/**
 * Login response data structure
 */
interface LoginResponse {
  code: string;
  message: string;
  data: {
    token: string;
    token_type: string;
    expires_in: number;
    user: {
      username: string;
      email: string;
      role: string;
    };
  };
}

/**
 * CSRF token response data structure
 */
interface CsrfResponse {
  code: string;
  message: string;
  data: {
    csrf_token: string;
    token_type: string;
    expires_in: number;
  };
}

/**
 * Authentication tokens
 */
export interface AuthTokens {
  jwtToken: string;
  csrfToken: string;
  user: {
    username: string;
    email: string;
    role: string;
  };
}

/**
 * Login options
 */
export interface LoginOptions {
  /**
   * Username for login (defaults to 'admin')
   */
  username?: string;

  /**
   * Password for login (defaults to 'admin123' or env.ADMIN_PASSWORD)
   */
  password?: string;

  /**
   * Whether to fetch CSRF token after login (defaults to true)
   */
  fetchCsrfToken?: boolean;

  /**
   * Whether to store tokens in localStorage (defaults to true)
   */
  storeTokens?: boolean;
}

/**
 * Login and get authentication tokens (JWT + CSRF)
 *
 * This function performs the complete login flow:
 * 1. POST to /api/v1/auth/login with form data to get JWT token
 * 2. GET from /api/csrf-token to get CSRF token
 * 3. Optionally store tokens in localStorage for use in UI tests
 *
 * @param request - Playwright APIRequestContext for making HTTP requests
 * @param options - Login options (credentials, token storage, etc.)
 * @returns Authentication tokens (JWT + CSRF + user info)
 *
 * @example
 * ```typescript
 * const tokens = await loginAndGetCsrfToken(request);
 * console.log('JWT Token:', tokens.jwtToken);
 * console.log('CSRF Token:', tokens.csrfToken);
 * console.log('User:', tokens.user);
 * ```
 *
 * @example
 * ```typescript
 * // Login with custom credentials
 * const tokens = await loginAndGetCsrfToken(request, {
 *   username: 'testuser',
 *   password: 'testpass',
 * });
 * ```
 */
export async function loginAndGetCsrfToken(
  request: APIRequestContext,
  options: LoginOptions = {}
): Promise<AuthTokens> {
  const {
    username = AUTH_CONFIG.defaultCredentials.username,
    password = AUTH_CONFIG.defaultCredentials.password,
    fetchCsrfToken = true,
    storeTokens = true,
  } = options;

  // Step 1: Login to get JWT token
  const loginUrl = `${AUTH_CONFIG.baseURL}${AUTH_CONFIG.loginPath}`;
  const loginFormData = new URLSearchParams({
    username,
    password,
  });

  const loginResponse = await request.post(loginUrl, {
    data: loginFormData.toString(),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  if (!loginResponse.ok()) {
    throw new Error(
      `Login failed with status ${loginResponse.status()}: ${await loginResponse.text()}`
    );
  }

  const loginData: LoginResponse = await loginResponse.json();
  const jwtToken = loginData.data.token;
  const user = loginData.data.user;

  // Step 2: Get CSRF token
  let csrfToken = '';
  if (fetchCsrfToken) {
    const csrfUrl = `${AUTH_CONFIG.baseURL}${AUTH_CONFIG.csrfPath}`;
    const csrfResponse = await request.get(csrfUrl);

    if (!csrfResponse.ok()) {
      console.warn(`Failed to fetch CSRF token: ${csrfResponse.status()}`);
      // Continue without CSRF token in test environment
    } else {
      const csrfData: CsrfResponse = await csrfResponse.json();
      csrfToken = csrfData.data.csrf_token;
    }
  }

  // Step 3: Store tokens if requested
  if (storeTokens) {
    // Note: This returns the storage state, which can be used with page.route()
    // or passed to browser.newContext() in Playwright tests
    // For now, we return the tokens and let the test decide how to use them
  }

  return {
    jwtToken,
    csrfToken,
    user,
  };
}

/**
 * Setup authentication state for a Page object
 *
 * This function configures a Playwright Page object with authentication tokens
 * by adding them to localStorage and setting default headers.
 *
 * @param page - Playwright Page object
 * @param tokens - Authentication tokens from loginAndGetCsrfToken()
 *
 * @example
 * ```typescript
 * const page = await browser.newPage();
 * const tokens = await loginAndGetCsrfToken(request);
 * await setupAuthForPage(page, tokens);
 * // Now the page is authenticated and can make API requests
 * ```
 */
export async function setupAuthForPage(page: Page, tokens: AuthTokens): Promise<void> {
  // Navigate to base URL first (required for localStorage to be accessible)
  await page.goto(AUTH_CONFIG.baseURL.replace('8000', '3001')); // Frontend URL
  await page.waitForLoadState('domcontentloaded');

  // Store JWT token in localStorage
  await page.evaluate(([token, user]) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  }, [tokens.jwtToken, tokens.user]);

  // Set default headers for API requests
  await page.route('**/api/**', async (route) => {
    const headers = {
      ...route.request().headers(),
      'Authorization': `Bearer ${tokens.jwtToken}`,
    };

    // Add CSRF token header for modifying requests
    if (tokens.csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(route.request().method())) {
      headers['x-csrf-token'] = tokens.csrfToken;
    }

    // Continue with modified headers
    route.continue({ headers });
  });
}

/**
 * Complete login flow for E2E tests
 *
 * This is a convenience function that combines loginAndGetCsrfToken and
 * setupAuthForPage for the common case of authenticating a page in tests.
 *
 * @param request - Playwright APIRequestContext
 * @param page - Playwright Page object
 * @param options - Login options
 * @returns Authentication tokens
 *
 * @example
 * ```typescript
 * test.beforeEach(async ({ page, request }) => {
 *   await loginAndSetupAuth(request, page);
 *   // Page is now authenticated and ready for testing
 * });
 * ```
 */
export async function loginAndSetupAuth(
  request: APIRequestContext,
  page: Page,
  options?: LoginOptions
): Promise<AuthTokens> {
  const tokens = await loginAndGetCsrfToken(request, options);
  await setupAuthForPage(page, tokens);
  return tokens;
}

/**
 * Clear authentication state from a Page object
 *
 * @param page - Playwright Page object
 */
export async function clearAuth(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  });
}

/**
 * Legacy login function (UI-based)
 *
 * @deprecated Use loginAndSetupAuth() instead for better reliability
 *
 * This function performs login by interacting with the UI, which is slower
 * and more brittle than the API-based approach. It's kept for backward
 * compatibility with existing tests.
 *
 * @param page - Playwright Page object
 * @param username - Username (defaults to 'admin')
 * @param password - Password (defaults to 'admin123')
 */
export async function loginUI(
  page: Page,
  username: string = AUTH_CONFIG.defaultCredentials.username,
  password: string = AUTH_CONFIG.defaultCredentials.password
): Promise<void> {
  const frontendURL = AUTH_CONFIG.baseURL.replace('8000', '3001');
  await page.goto(`${frontendURL}/login`);
  await page.waitForLoadState('domcontentloaded');

  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');

  await page.waitForURL('**/dashboard');
}
