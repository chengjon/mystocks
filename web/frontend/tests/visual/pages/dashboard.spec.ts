import { test, expect } from '../fixtures/visual.fixture';
import { validateGoldTheme, validateMarketColors } from '../utils/helpers';

const ARTDECO_GOLD_PRIMARY = '#D4AF37';
const MARKET_UP = '#FF5252';
const MARKET_DOWN = '#00E676';

const DASHBOARD_ROOT = '.artdeco-dashboard';
const FUND_FLOW_CARD = '.fund-flow-overview';
const MARKET_INDICATORS_CARD = '.market-indicators';
const SENTIMENT_CARD = '.sentiment-card';
const STATUS_CARD = '.market-status-card';

const VISUAL_USER = {
  id: 1,
  username: 'visual-admin',
  email: 'visual-admin@example.com',
  role: 'admin',
  permissions: [],
};

test.describe('Dashboard Panels - ArtDeco V3.0 Theme', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(({ user }) => {
      localStorage.setItem('auth_token', 'visual-dashboard-token');
      localStorage.setItem('auth_user', JSON.stringify(user));
    }, { user: VISUAL_USER });

    await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
      const url = new URL(route.request().url());

      if (url.pathname === '/api/health/ready') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'system ready',
            request_id: 'visual-dashboard-ready',
            data: { status: 'ready' },
          }),
        });
        return;
      }

      if (url.pathname === '/api/csrf-token') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: { csrf_token: 'visual-dashboard-csrf' } }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [] }),
      });
    });

    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);
    await expect(page.locator(DASHBOARD_ROOT)).toBeVisible({ timeout: 15000 });
    await validateGoldTheme(page);
  });

  test('Fund flow overview renders key metrics and chart shell', async ({ page }) => {
    const card = page.locator(FUND_FLOW_CARD);

    await expect(card).toBeVisible();
    await expect(card).toContainText('市场资金流向概览');
    await expect(card).toContainText('沪股通净流入');
    await expect(card.locator('.artdeco-chart-container')).toBeVisible();
  });

  test('Market indicators panel renders major indexes and trend chart shell', async ({ page }) => {
    const card = page.locator(MARKET_INDICATORS_CARD);

    await expect(card).toBeVisible();
    await expect(card).toContainText('主要市场指标');
    await expect(card).toContainText('上证指数');
    await expect(card).toContainText('深证成指');
    await expect(card.locator('.artdeco-chart-container')).toBeVisible();
  });

  test('Sentiment and market status cards render together', async ({ page }) => {
    const sentimentCard = page.locator(SENTIMENT_CARD);
    const statusCard = page.locator(STATUS_CARD);

    await expect(sentimentCard).toBeVisible();
    await expect(sentimentCard).toContainText('资金流向');
    await expect(statusCard).toBeVisible();
    await expect(statusCard).toContainText('市场状态');

    await validateMarketColors(page);
  });

  test('Dashboard full layout shows all primary panels', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);
    await expect(page.locator(DASHBOARD_ROOT)).toBeVisible({ timeout: 15000 });

    await expect(page.locator(FUND_FLOW_CARD)).toBeVisible();
    await expect(page.locator(MARKET_INDICATORS_CARD)).toBeVisible();
    await expect(page.locator(SENTIMENT_CARD)).toBeVisible();
    await expect(page.locator(STATUS_CARD)).toBeVisible();
  });
});

test.describe('ArtDeco Theme Colors', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(({ user }) => {
      localStorage.setItem('auth_token', 'visual-dashboard-token');
      localStorage.setItem('auth_user', JSON.stringify(user));
    }, { user: VISUAL_USER });

    await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
      const url = new URL(route.request().url());

      if (url.pathname === '/api/health/ready') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: { status: 'ready' } }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [] }),
      });
    });
  });

  test('Gold primary color is applied', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);
    expect(ARTDECO_GOLD_PRIMARY).toBe('#D4AF37');
  });

  test('Market colors (Red/Green) are correct for A股', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    await validateMarketColors(page);
    expect(MARKET_UP).toBe('#FF5252');
    expect(MARKET_DOWN).toBe('#00E676');
  });
});
