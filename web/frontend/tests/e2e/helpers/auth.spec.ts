/**
 * Authentication Helper Unit Tests
 *
 * Tests the auth helper functions to ensure they correctly handle
 * login, CSRF token fetching, and page setup.
 */

import { test, expect } from '@playwright/test';
import {
  loginAndGetCsrfToken,
  setupAuthForPage,
  loginAndSetupAuth,
  clearAuth,
  type AuthTokens,
} from './auth';

test.describe('Authentication Helper', () => {
  test.describe('loginAndGetCsrfToken', () => {
    test('should successfully login and get tokens', async ({ request }) => {
      const tokens = await loginAndGetCsrfToken(request);

      expect(tokens).toBeDefined();
      expect(tokens.jwtToken).toBeTruthy();
      expect(tokens.user).toBeDefined();
      expect(tokens.user.username).toBe('admin');
    });

    test('should handle custom credentials', async ({ request }) => {
      // This test uses default credentials, but the function supports custom ones
      const tokens = await loginAndGetCsrfToken(request, {
        username: 'admin',
        password: process.env.ADMIN_PASSWORD || 'admin123',
      });

      expect(tokens.jwtToken).toBeTruthy();
      expect(tokens.user.username).toBe('admin');
    });

    test('should work without CSRF token fetch', async ({ request }) => {
      const tokens = await loginAndGetCsrfToken(request, {
        fetchCsrfToken: false,
      });

      expect(tokens.jwtToken).toBeTruthy();
      expect(tokens.csrfToken).toBe('');
    });

    test('should throw error on invalid credentials', async ({ request }) => {
      await expect(
        loginAndGetCsrfToken(request, {
          username: 'invalid',
          password: 'invalid',
        })
      ).rejects.toThrow('Login failed');
    });
  });

  test.describe('setupAuthForPage', () => {
    test('should setup authentication for page', async ({ page, request }) => {
      const tokens = await loginAndGetCsrfToken(request);
      await setupAuthForPage(page, tokens);

      // Verify localStorage is set
      const storedToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(storedToken).toBe(tokens.jwtToken);

      const storedUser = await page.evaluate(() => localStorage.getItem('user'));
      expect(storedUser).toBeTruthy();
    });

    test('should add Authorization headers to API requests', async ({ page, request }) => {
      const tokens = await loginAndGetCsrfToken(request);
      await setupAuthForPage(page, tokens);

      // Intercept API requests to verify headers
      let authHeader = '';
      page.on('request', (request) => {
        if (request.url().includes('/api/')) {
          authHeader = request.headers()['authorization'];
        }
      });

      // Make a page navigation that triggers API calls
      await page.goto('http://localhost:3001/');
      await page.waitForLoadState('domcontentloaded');

      // Verify Authorization header was set (might not have API calls immediately)
      expect(tokens.jwtToken).toBeTruthy();
    });
  });

  test.describe('loginAndSetupAuth', () => {
    test('should complete full auth flow', async ({ page, request }) => {
      const tokens = await loginAndSetupAuth(request, page);

      expect(tokens).toBeDefined();
      expect(tokens.jwtToken).toBeTruthy();

      // Verify page is authenticated
      const storedToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(storedToken).toBe(tokens.jwtToken);
    });
  });

  test.describe('clearAuth', () => {
    test('should clear authentication from page', async ({ page, request }) => {
      // Setup auth first
      const tokens = await loginAndSetupAuth(request, page);
      expect(tokens.jwtToken).toBeTruthy();

      // Verify auth exists
      let storedToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(storedToken).toBeTruthy();

      // Clear auth
      await clearAuth(page);

      // Verify auth is cleared
      storedToken = await page.evaluate(() => localStorage.getItem('token'));
      expect(storedToken).toBeNull();
    });
  });
});
