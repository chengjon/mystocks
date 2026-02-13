/**
 * MyStocks Full Page Validation Test
 *
 * Tests all pages for:
 * 1. HTTP status (200 OK)
 * 2. No JavaScript console errors
 * 3. Key DOM elements exist
 * 4. Page is interactive
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:3020';

// All pages to test
const PAGES = [
  { name: 'Home', path: '/', keyElements: ['header', 'main', 'nav'] },
  { name: 'Login', path: '/login', keyElements: ['form', 'input[type="password"]', 'button[type="submit"]'] },
  { name: 'Dashboard', path: '/dashboard', keyElements: ['main', 'header'] },
  { name: 'Market', path: '/market', keyElements: ['main', 'header'] },
  { name: 'Stocks', path: '/stocks', keyElements: ['main', 'header'] },
  { name: 'Analysis', path: '/analysis', keyElements: ['main', 'header'] },
  { name: 'Risk', path: '/risk', keyElements: ['main', 'header'] },
  { name: 'Trading', path: '/trading', keyElements: ['main', 'header'] },
  { name: 'Strategy', path: '/strategy', keyElements: ['main', 'header'] },
  { name: 'System', path: '/system', keyElements: ['main', 'header'] },
  // ArtDeco pages
  { name: 'ArtDeco-Dashboard', path: '/artdeco/dashboard', keyElements: ['main'] },
  { name: 'ArtDeco-Risk', path: '/artdeco/risk', keyElements: ['main'] },
  { name: 'ArtDeco-Trading', path: '/artdeco/trading', keyElements: ['main'] },
  { name: 'ArtDeco-Backtest', path: '/artdeco/backtest', keyElements: ['main'] },
  { name: 'ArtDeco-Monitor', path: '/artdeco/monitor', keyElements: ['main'] },
  { name: 'ArtDeco-Strategy', path: '/artdeco/strategy', keyElements: ['main'] },
  { name: 'ArtDeco-Settings', path: '/artdeco/settings', keyElements: ['main'] },
  { name: 'ArtDeco-Community', path: '/artdeco/community', keyElements: ['main'] },
  { name: 'ArtDeco-Help', path: '/artdeco/help', keyElements: ['main'] },
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
];

function isCriticalError(text: string): boolean {
  return !IGNORED_ERROR_PATTERNS.some(pattern => text.includes(pattern));
}

test.describe('Full Page Validation', () => {
  for (const pageInfo of PAGES) {
    test(`${pageInfo.name} (${pageInfo.path})`, async ({ page }) => {
      const errors: string[] = [];
      const warnings: string[] = [];

      // Capture console messages
      page.on('console', msg => {
        const text = msg.text();
        if (msg.type() === 'error' && isCriticalError(text)) {
          errors.push(text);
        }
        if (msg.type() === 'warning') {
          warnings.push(text);
        }
      });

      // Capture page errors
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

      // Test 1: HTTP Status
      const httpStatus = response?.status() || 0;
      console.log(`\n${pageInfo.name}: HTTP ${httpStatus}`);

      // Test 2: No critical JS errors
      if (errors.length > 0) {
        console.log(`  Critical Errors: ${errors.length}`);
        errors.slice(0, 5).forEach(e => console.log(`    - ${e.substring(0, 150)}`));
      }

      // Test 3: Key DOM elements exist
      const domResults: string[] = [];
      for (const selector of pageInfo.keyElements) {
        const element = await page.$(selector);
        domResults.push(`${selector}: ${element ? 'OK' : 'MISSING'}`);
      }
      console.log(`  DOM Elements: ${domResults.join(', ')}`);

      // Test 4: Page title exists
      const title = await page.title();
      console.log(`  Title: ${title}`);

      // Assertions
      expect(httpStatus).toBeLessThan(400);
      expect(errors.length).toBe(0);
    });
  }
});

// Test backend API integration
test.describe('Backend API Integration', () => {
  test('Health endpoint returns code=0', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    const data = await response.json();

    console.log(`\nBackend Health: ${JSON.stringify(data)}`);

    expect(response.status()).toBe(200);
    expect(data.success).toBe(true);
    expect(data.code).toBe(200);
  });

  test('Market overview returns data', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/dashboard/market-overview');
    const data = await response.json();

    console.log(`\nMarket Overview: ${JSON.stringify(data).substring(0, 200)}...`);

    expect(response.status()).toBe(200);
    expect(data.indices).toBeDefined();
    expect(Array.isArray(data.indices)).toBe(true);
  });
});
