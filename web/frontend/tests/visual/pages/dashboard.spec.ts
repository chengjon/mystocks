import { test, expect } from '../fixtures/visual.fixture';
import { dismissOverlay, validateGoldTheme, validateMarketColors } from '../utils/helpers';

test.use({ serviceWorkers: 'block' });

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
  permissions: ['*'],
};

async function seedVisualSession(page: Parameters<typeof test>[0]['page']) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_token', 'visual-dashboard-token');
    localStorage.setItem('token', 'visual-dashboard-token');
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('user', JSON.stringify(user));
  }, VISUAL_USER);
}

async function dismissVersionNotifications(page: Parameters<typeof test>[0]['page']) {
  await page.evaluate(() => {
    for (const notification of document.querySelectorAll('.el-notification')) {
      notification.remove();
    }
  });
  await dismissOverlay(page);
}

async function stubDashboardApis(page: Parameters<typeof test>[0]['page']) {
  await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
    const url = new URL(route.request().url());

    if (url.pathname === '/api/health' || url.pathname === '/api/health/ready') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'system ready',
          request_id: 'visual-dashboard-ready',
          data: { status: 'ready', version: '1.0.0' },
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

    if (url.pathname === '/api/auth/me' || url.pathname === '/api/v1/auth/me') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-auth-me',
          data: VISUAL_USER,
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/market/quotes') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-market',
          data: [
            { symbol: '000001.SH', latest_price: 3150.42, change_percent: 0.86, volume: 123456789 },
            { symbol: '399001.SZ', latest_price: 10234.55, change_percent: 1.12, volume: 987654321 },
            { symbol: '399006.SZ', latest_price: 1987.65, change_percent: -0.24, volume: 456789123 },
          ],
        }),
      });
      return;
    }

    if (url.pathname === '/api/akshare/market/fund-flow/hsgt-summary') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-fund-flow',
          data: [
            { item: '沪股通', net_inflow: 18.6, netFlow: 18.6, change: 2.1 },
            { item: '深股通', net_inflow: 12.3, netFlow: 12.3, change: 1.4 },
            { item: '北向资金', net_inflow: 30.9, netFlow: 30.9, monthly: 128.4 },
          ],
        }),
      });
      return;
    }

    if (url.pathname === '/api/akshare/market/fund-flow/big-deal') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-big-deal',
          data: [
            { code: '600519.SH', name: '贵州茅台', amount: 15.2, change: 2.6 },
            { code: '000858.SZ', name: '五粮液', amount: 12.8, change: 1.9 },
            { code: '601318.SH', name: '中国平安', amount: -6.3, change: -1.2 },
          ],
        }),
      });
      return;
    }

    if (
      url.pathname === '/api/v2/market/sector/fund-flow'
      || url.pathname === '/api/akshare/market/sector/fund-flow-ranking'
      || url.pathname === '/api/akshare/market/sector/hot-ranking'
    ) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-sector-flow',
          data: [
            { name: '人工智能', change: 3.4, amount: 22.5 },
            { name: '半导体', change: 2.8, amount: 18.1 },
            { name: '高端制造', change: 1.9, amount: 14.3 },
          ],
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/strategy/active') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-strategies',
          data: [{ id: 1 }, { id: 2 }, { id: 3 }],
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/strategy/strategies') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-strategies',
          data: [{ id: 1 }, { id: 2 }, { id: 3 }],
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/risk/position-risk' || url.pathname === '/api/v1/trade/positions') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-position-risk',
          data: {
            totalValue: 1280000,
            totalPnL: 32650,
            pnlPercent: 2.55,
            maxDrawdown: 4.2,
            riskLevel: 'medium',
            riskLevelText: '中等',
            positions: [
              { symbol: '600519.SH', market_value: '875000.00', profit_loss_percent: 6.06 },
              { symbol: '000858.SZ', market_value: '150000.00', profit_loss_percent: 3.45 },
            ],
          },
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/system/health') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-system-health',
          data: [
            { label: 'API', value: '99.98%', status: 'good' },
            { label: 'DB', value: '12ms', status: 'good' },
            { label: 'WS', value: 'online', status: 'good' },
          ],
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/technical-indicators') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-indicators',
          data: {
            '000001.SH': [
              { name: 'RSI', value: '56.4', trend: 'rise', signal: '偏强' },
              { name: 'MACD', value: '1.32', trend: 'rise', signal: '金叉' },
              { name: 'KDJ', value: '68.1', trend: 'neutral', signal: '观望' },
              { name: 'BOLL', value: '中轨上方', trend: 'rise', signal: '突破' },
            ],
          },
        }),
      });
      return;
    }

    if (url.pathname === '/api/v1/market/kline') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'visual-dashboard-kline',
          data: Array.from({ length: 40 }, (_, index) => ({ close: 3000 + index * 5 })),
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: [] }),
    });
  });
}

test.describe('Dashboard Panels - ArtDeco V3.0 Theme', () => {
  test.beforeEach(async ({ page }) => {
    await stubDashboardApis(page);
    await seedVisualSession(page);
    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    await dismissVersionNotifications(page);
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
    await dismissVersionNotifications(page);
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
    await stubDashboardApis(page);
    await seedVisualSession(page);
  });

  test('Gold primary color is applied', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    await dismissVersionNotifications(page);
    await validateGoldTheme(page);
    expect(ARTDECO_GOLD_PRIMARY).toBe('#D4AF37');
  });

  test('Market colors (Red/Green) are correct for A股', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
    await dismissVersionNotifications(page);
    await validateMarketColors(page);
    expect(MARKET_UP).toBe('#FF5252');
    expect(MARKET_DOWN).toBe('#00E676');
  });
});
