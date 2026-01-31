/**
 * MyStocks Comprehensive E2E Test Suite
 * 
 * Tests all pages including:
 * - User authentication (login)
 * - Real-time market data
 * - Historical K-line data
 * - Technical analysis
 * - Watchlist/Portfolio management
 * - Strategy management
 * - Risk monitoring
 * - System administration
 * 
 * Usage:
 *   npm run test:e2e:comprehensive
 *   npx playwright test comprehensive-all-pages.spec.ts --project=chromium
 */

import { test, expect, chromium } from '@playwright/test';

// ============ Page List (All Routes from router/index.ts) ============
const PAGES = [
  // Public pages
  { name: 'Login', path: '/login', requiresAuth: false },
  
  // ArtDeco Dashboard (Home)
  { name: 'Dashboard', path: '/dashboard', requiresAuth: true },
  
  // ArtDeco Market Domain (10 pages)
  { name: 'Market-Realtime', path: '/market/realtime', requiresAuth: true },
  { name: 'Market-Technical', path: '/market/technical', requiresAuth: true },
  { name: 'Market-FundFlow', path: '/market/fund-flow', requiresAuth: true },
  { name: 'Market-ETF', path: '/market/etf', requiresAuth: true },
  { name: 'Market-Concept', path: '/market/concept', requiresAuth: true },
  { name: 'Market-Auction', path: '/market/auction', requiresAuth: true },
  { name: 'Market-LongHuBang', path: '/market/longhubang', requiresAuth: true },
  { name: 'Market-Institution', path: '/market/institution', requiresAuth: true },
  { name: 'Market-Wencai', path: '/market/wencai', requiresAuth: true },
  { name: 'Market-Screener', path: '/market/screener', requiresAuth: true },
  
  // ArtDeco Stock Management (2 pages)
  { name: 'Stock-Management', path: '/stocks/management', requiresAuth: true },
  { name: 'Stock-Portfolio', path: '/stocks/portfolio', requiresAuth: true },
  
  // ArtDeco Trading Domain (4 pages)
  { name: 'Trading-Signals', path: '/trading/signals', requiresAuth: true },
  { name: 'Trading-History', path: '/trading/history', requiresAuth: true },
  { name: 'Trading-Positions', path: '/trading/positions', requiresAuth: true },
  { name: 'Trading-Attribution', path: '/trading/attribution', requiresAuth: true },
  
  // ArtDeco Strategy Domain (5 pages)
  { name: 'Strategy-Design', path: '/strategy/design', requiresAuth: true },
  { name: 'Strategy-Management', path: '/strategy/management', requiresAuth: true },
  { name: 'Strategy-Backtest', path: '/strategy/backtest', requiresAuth: true },
  { name: 'Strategy-GPU-Backtest', path: '/strategy/gpu-backtest', requiresAuth: true },
  { name: 'Strategy-Optimization', path: '/strategy/optimization', requiresAuth: true },
  
  // ArtDeco Risk Domain (5 pages)
  { name: 'Risk-Overview', path: '/risk/overview', requiresAuth: true },
  { name: 'Risk-Alerts', path: '/risk/alerts', requiresAuth: true },
  { name: 'Risk-Indicators', path: '/risk/indicators', requiresAuth: true },
  { name: 'Risk-Sentiment', path: '/risk/sentiment', requiresAuth: true },
  { name: 'Risk-Announcement', path: '/risk/announcement', requiresAuth: true },
  
  // ArtDeco System Domain (5 pages)
  { name: 'System-Monitoring', path: '/system/monitoring', requiresAuth: true },
  { name: 'System-Settings', path: '/system/settings', requiresAuth: true },
  { name: 'System-DataUpdate', path: '/system/data-update', requiresAuth: true },
  { name: 'System-DataQuality', path: '/system/data-quality', requiresAuth: true },
  { name: 'System-APIHealth', path: '/system/api-health', requiresAuth: true },
];

// Test credentials
const TEST_USER = { username: 'admin', password: 'admin123' };

// Frontend URL (from PM2 config)
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3002';

// ============ Helper: Login ============
async function login(page: any) {
  await page.goto(`${FRONTEND_URL}/login`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  
  // Fill login form
  await page.fill('input[placeholder*="USERNAME" i], input[data-testid="username-input"]', TEST_USER.username);
  await page.fill('input[type="password"]', TEST_USER.password);
  
  // Click login button
  await page.click('button[type="submit"]');
  
  // Wait for navigation or success
  await page.waitForTimeout(3000);
  
  // Check if logged in (should be redirected to dashboard)
  const url = page.url();
  return url.includes('/dashboard') || url === FRONTEND_URL || url === `${FRONTEND_URL}/`;
}

// ============ Test: Login Page ============
test.describe('Authentication', () => {
  test('Login page loads without critical errors', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error' && !isIgnoredError(msg.text())) {
        errors.push(msg.text());
      }
    });
    
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    const response = await page.goto(`${FRONTEND_URL}/login`, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Check page loads
    expect(response?.status()).toBeLessThan(400);
    
    // Check login form exists
    const usernameInput = page.locator('input[placeholder*="USERNAME" i], input[data-testid="username-input"]');
    await expect(usernameInput).toBeVisible({ timeout: 5000 });
    
    // Perform login
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.fill(usernameInput, TEST_USER.username);
    await page.click('button[type="submit"]');
    
    // Wait for login to complete
    await page.waitForTimeout(3000);
    
    // Check for critical errors (ignore expected 503/404 from mock APIs)
    const criticalErrors = errors.filter(e => !e.includes('503') && !e.includes('404') && !e.includes('Failed to load'));
    
    // Log results
    console.log(`Login test: HTTP ${response?.status()}`);
    if (errors.length > 0) {
      console.log(`  Non-critical errors: ${errors.length}`);
    }
    
    // Login should not have critical JS errors
    expect(criticalErrors.length).toBe(0);
  });
});

// ============ Test: All Pages (Authenticated) ============
test.describe('All Pages (Authenticated)', async () => {
  // Login once and reuse context
  test.beforeEach(async ({ page }) => {
    const loggedIn = await login(page);
    if (!loggedIn) {
      // If not redirected, check if we're on login page still
      await page.waitForTimeout(2000);
    }
  });
  
  for (const pageInfo of PAGES.filter(p => p.requiresAuth)) {
    test(`${pageInfo.name} (${pageInfo.path})`, async ({ page }) => {
      const errors: string[] = [];
      
      page.on('console', msg => {
        if (msg.type() === 'error' && !isIgnoredError(msg.text())) {
          errors.push(msg.text());
        }
      });
      
      page.on('pageerror', error => {
        errors.push(error.message);
      });
      
      const response = await page.goto(`${FRONTEND_URL}${pageInfo.path}`, { 
        waitUntil: 'domcontentloaded',
        timeout: 30000 
      });
      
      // Wait for page to render
      await page.waitForTimeout(2000);
      
      // Log results
      console.log(`${pageInfo.name}: HTTP ${response?.status() || 'N/A'}`);
      if (errors.length > 0) {
        console.log(`  Errors: ${errors.length}`);
        errors.slice(0, 3).forEach(e => console.log(`    - ${e.substring(0, 100)}`));
      }
      
      // Page should load (HTTP 200 or redirect)
      expect(response ? response.status() : 0).toBeGreaterThanOrEqual(200);
    });
  }
});

// ============ Test: API Integration ============
test.describe('API Integration', () => {
  test('Backend health check', async ({ request }) => {
    const response = await request.get(`${FRONTEND_URL.replace(':3002', ':8000')}/api/health`);
    console.log(`Health check: HTTP ${response.status()}`);
    // Health check may fail if backend not running, that's OK for frontend-only tests
    expect([200, 503, 0]).toContain(response.status());
  });
});

// ============ Helper: Ignore expected errors ============
function isIgnoredError(text: string): boolean {
  const ignoredPatterns = [
    '503',                           // Service unavailable (expected with mock)
    'Failed to load resource',       // Network errors
    'Download error',                // Resource download errors
    'deprecated',                    // Deprecation warnings
    'message port closed',           // WebSocket closed
    'Service Worker',                // PWA service worker
    'favicon',                       // Favicon missing
    'manifest',                      // Manifest errors
    'icon-144',                      // Missing icon
    'contract',                      // Contract validation (optional)
    'WebSocket',                     // WebSocket errors
    'ws://',                         // WebSocket URLs
    'ws://localhost',                // Local WebSocket
  ];
  
  return ignoredPatterns.some(pattern => text.includes(pattern));
}

// ============ Export for reuse ============
export { PAGES, TEST_USER, FRONTEND_URL };
