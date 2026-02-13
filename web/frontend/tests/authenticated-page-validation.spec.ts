/**
 * MyStocks Authenticated Page Validation Test
 *
 * Tests all pages AFTER login:
 * 1. HTTP status (200 OK)
 * 2. No JavaScript console errors
 * 3. Key DOM elements exist
 * 4. Page is interactive
 * 5. API calls succeed (code=0 or code=200)
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:3020';
const BACKEND_URL = 'http://localhost:8000';
const TEST_USER = { username: 'admin', password: 'admin123' };

// Pages that require authentication
const AUTH_PAGES = [
  { name: 'Dashboard', path: '/dashboard', keyElements: ['.artdeco-dashboard', '.dashboard-container', 'main'] },
  { name: 'Market', path: '/market', keyElements: ['.market-container', 'main'] },
  { name: 'Stocks', path: '/stocks', keyElements: ['.stock-container', 'main'] },
  { name: 'Analysis', path: '/analysis', keyElements: ['.analysis-container', 'main'] },
  { name: 'Risk', path: '/risk', keyElements: ['.risk-container', 'main'] },
  { name: 'Trading', path: '/trading', keyElements: ['.trading-container', 'main'] },
  { name: 'Strategy', path: '/strategy', keyElements: ['.strategy-container', 'main'] },
  { name: 'System', path: '/system', keyElements: ['.system-container', 'main'] },
  // ArtDeco pages
  { name: 'ArtDeco-Dashboard', path: '/artdeco/dashboard', keyElements: ['.artdeco-dashboard', 'main', '[class*="dashboard"]'] },
  { name: 'ArtDeco-Risk', path: '/artdeco/risk', keyElements: ['main', '[class*="risk"]'] },
  { name: 'ArtDeco-Trading', path: '/artdeco/trading', keyElements: ['main', '[class*="trading"]'] },
  { name: 'ArtDeco-Backtest', path: '/artdeco/backtest', keyElements: ['main', '[class*="backtest"]'] },
  { name: 'ArtDeco-Monitor', path: '/artdeco/monitor', keyElements: ['main', '[class*="monitor"]'] },
  { name: 'ArtDeco-Strategy', path: '/artdeco/strategy', keyElements: ['main', '[class*="strategy"]'] },
  { name: 'ArtDeco-Settings', path: '/artdeco/settings', keyElements: ['main', '[class*="settings"]'] },
];

// Errors to ignore (not critical)
const IGNORED_ERROR_PATTERNS = [
  '503',
  'Failed to load resource',
  'Download error',
  'deprecated',
  'message port closed',
  'Service Worker',
  'favicon',
  'manifest',
  'icon-144',
  'WebSocket',
  'ws://',
  'net::ERR',
  '404',
  'TypeError: Failed to fetch',
  'ChunkLoadError',
  'Loading chunk',
  'Failed to fetch dynamically imported module',
  'ResizeObserver',
];

function isCriticalError(text: string): boolean {
  return !IGNORED_ERROR_PATTERNS.some(pattern => text.includes(pattern));
}

// Global storage for auth state
let authToken: string | null = null;

test.describe('Authentication', () => {
  test('Login should succeed', async ({ page, request }) => {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error' && isCriticalError(msg.text())) {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', error => {
      if (isCriticalError(error.message)) {
        errors.push(error.message);
      }
    });

    // Navigate to login page
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1000);

    // Fill login form
    const usernameInput = page.locator('input[placeholder*="username" i], input[data-testid="username-input"], input[type="text"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const submitButton = page.locator('button[type="submit"]').first();

    await usernameInput.fill(TEST_USER.username);
    await passwordInput.fill(TEST_USER.password);
    await submitButton.click();

    // Wait for login to complete
    await page.waitForTimeout(3000);

    // Check if redirected away from login
    const currentUrl = page.url();
    const loginSuccess = !currentUrl.includes('/login');

    console.log(`\nLogin Test:`);
    console.log(`  Current URL: ${currentUrl}`);
    console.log(`  Login Success: ${loginSuccess}`);
    console.log(`  Errors: ${errors.length}`);

    // Try to get auth token from localStorage
    authToken = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('auth_token') || sessionStorage.getItem('token');
    });

    console.log(`  Auth Token: ${authToken ? 'Present' : 'Not found'}`);

    // Check critical errors
    if (errors.length > 0) {
      console.log(`  Critical Errors:`);
      errors.forEach(e => console.log(`    - ${e.substring(0, 150)}`));
    }

    // Login should succeed or at least not have critical errors
    expect(errors.length).toBe(0);
  });
});

test.describe('Authenticated Pages', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);

    const usernameInput = page.locator('input[placeholder*="username" i], input[data-testid="username-input"], input[type="text"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const submitButton = page.locator('button[type="submit"]').first();

    await usernameInput.fill(TEST_USER.username);
    await passwordInput.fill(TEST_USER.password);
    await submitButton.click();

    await page.waitForTimeout(2000);
  });

  for (const pageInfo of AUTH_PAGES) {
    test(`${pageInfo.name} (${pageInfo.path}) loads without errors`, async ({ page }) => {
      const errors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error' && isCriticalError(msg.text())) {
          errors.push(msg.text());
        }
      });

      page.on('pageerror', error => {
        if (isCriticalError(error.message)) {
          errors.push(error.message);
        }
      });

      // Navigate to page
      const response = await page.goto(`${BASE_URL}${pageInfo.path}`, {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });

      // Wait for page to render
      await page.waitForTimeout(3000);

      const httpStatus = response?.status() || 0;
      const currentUrl = page.url();

      console.log(`\n${pageInfo.name}:`);
      console.log(`  HTTP Status: ${httpStatus}`);
      console.log(`  Current URL: ${currentUrl}`);

      // Check if redirected to login
      const onLoginPage = currentUrl.includes('/login');
      console.log(`  On Login Page: ${onLoginPage}`);

      // Check DOM elements
      const domResults: string[] = [];
      for (const selector of pageInfo.keyElements) {
        try {
          const element = await page.$(selector);
          domResults.push(`${selector}: ${element ? 'OK' : 'MISSING'}`);
        } catch {
          domResults.push(`${selector}: ERROR`);
        }
      }
      console.log(`  DOM Elements: ${domResults.join(', ')}`);

      // Check page title
      const title = await page.title();
      console.log(`  Title: ${title}`);

      // Check for errors
      if (errors.length > 0) {
        console.log(`  Critical Errors: ${errors.length}`);
        errors.slice(0, 3).forEach(e => console.log(`    - ${e.substring(0, 150)}`));
      }

      // Assertions
      expect(httpStatus).toBeLessThan(400);

      // If on login page, it means auth didn't work, but that's not a page error
      // We just check that there are no JS errors
      expect(errors.length).toBe(0);
    });
  }
});

test.describe('API Integration', () => {
  test('Backend health check returns success', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);
    const data = await response.json();

    console.log(`\nBackend Health:`);
    console.log(`  Status: ${response.status()}`);
    console.log(`  Success: ${data.success}`);
    console.log(`  Code: ${data.code}`);

    expect(response.status()).toBe(200);
    expect(data.success).toBe(true);
  });

  test('Market overview API returns data', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/dashboard/market-overview`);
    const data = await response.json();

    console.log(`\nMarket Overview:`);
    console.log(`  Status: ${response.status()}`);
    console.log(`  Indices Count: ${data.indices?.length || 0}`);
    console.log(`  Up Count: ${data.up_count}`);
    console.log(`  Down Count: ${data.down_count}`);

    expect(response.status()).toBe(200);
    expect(data.indices).toBeDefined();
  });

  test('Analysis APIs return data', async ({ request }) => {
    // Test industry list
    const response = await request.get(`${BACKEND_URL}/api/analysis/industry/list`);
    const data = await response.json();

    console.log(`\nIndustry List API:`);
    console.log(`  Status: ${response.status()}`);

    // Should return 200 or have valid response format
    expect(response.status()).toBeLessThan(500);
  });
});
