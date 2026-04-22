import { expect, test } from '../fixtures/visual.fixture';
import { validateGoldTheme } from '../utils/helpers';

test.describe.configure({ mode: 'serial' });

const VISUAL_USER = {
  id: 1,
  username: 'visual-risk-admin',
  email: 'visual-risk-admin@example.com',
  role: 'admin',
  permissions: ['*'],
};

const POSITIONS_ENDPOINTS = [
  '**/v1/trade/positions**',
  '**/api/v1/trade/positions**',
];

const positionsPayload = {
  success: true,
  code: 200,
  message: 'ok',
  request_id: 'visual-risk-positions',
  data: {
    positions: [
      {
        symbol: '600519.SH',
        symbol_name: '贵州茅台',
        market_value: '875000.00',
        profit_loss_percent: 6.06,
      },
      {
        symbol: '000858.SZ',
        symbol_name: '五粮液',
        market_value: '150000.00',
        profit_loss_percent: 3.45,
      },
      {
        symbol: '002594.SZ',
        symbol_name: '比亚迪',
        market_value: '120000.00',
        profit_loss_percent: -2.1,
      },
    ],
    total_market_value: '1145000.00',
    total_profit_loss: '48000.00',
    total_profit_loss_percent: 4.19,
  },
};

const emptyPositionsPayload = {
  success: true,
  code: 200,
  message: 'ok',
  request_id: 'visual-risk-empty',
  data: {
    positions: [],
    total_market_value: '0',
    total_profit_loss: '0',
    total_profit_loss_percent: '0',
  },
};

async function seedVisualSession(page: Parameters<typeof test>[0]['page']) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await page.evaluate((user) => {
    localStorage.setItem('auth_token', 'visual-risk-token');
    localStorage.setItem('auth_user', JSON.stringify(user));
  }, VISUAL_USER);
}

async function stubReadiness(page: Parameters<typeof test>[0]['page']) {
  for (const endpoint of ['**/api/health/ready', '**/health/ready']) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          code: 200,
          message: 'ready',
          data: { status: 'ready' },
        }),
      });
    });
  }
}

async function stubRiskEndpoints(
  page: Parameters<typeof test>[0]['page'],
  options?: {
    payload?: typeof positionsPayload
    requestId?: string
  }
) {
  const payload = options?.payload ?? positionsPayload;
  const requestId = options?.requestId ?? 'visual-risk-positions';

  await page.route('**/api/csrf-token', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: { csrf_token: 'visual-risk-csrf' },
      }),
    });
  });

  for (const endpoint of POSITIONS_ENDPOINTS) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: {
          'x-request-id': requestId,
        },
        body: JSON.stringify(payload),
      });
    });
  }
}

async function stabilizeVolatileText(page: Parameters<typeof test>[0]['page']) {
  await page.evaluate(() => {
    const setText = (selector: string, value: string) => {
      const element = document.querySelector<HTMLElement>(selector);
      if (element) {
        element.textContent = value;
      }
    };

    setText('.custom-tabs-trace span:last-child', 'REQ_ID: visual-risk-fixed');
    setText('.tabs-trace', 'REQ_ID: visual-risk-fixed');
    setText('.risk-content-shell-meta span:last-child', 'UPDATED: 2026-04-22 10:00:00');
    setText('.risk-footer-item:last-child span', '风险数据每5分钟自动更新 · 最后一次更新：2026-04-22 10:00:00');
  });
}

test.describe('Risk Management Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await seedVisualSession(page);
    await stubReadiness(page);
    await stubRiskEndpoints(page);
    await page.goto('/risk-management', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('.artdeco-page-template')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('.custom-tabs-trace')).toContainText('REQ_ID:');
    await expect(page.locator('#risk-panel-overview')).toBeVisible();
    await stabilizeVolatileText(page);
    await validateGoldTheme(page);
  });

  test('overview tab keeps risk shell stable', async ({ page }) => {
    await expect(page.locator('.risk-table')).toBeVisible();
    await expect(page.locator('.artdeco-page-template')).toHaveScreenshot('risk-management-overview.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 5000,
    });
  });

  test('stock tab keeps empty analysis panel stable', async ({ page }) => {
    await page.getByRole('tab', { name: '个股分析' }).click();
    await expect(page.locator('#risk-panel-stock')).toBeVisible();
    await expect(page.locator('#risk-panel-stock')).toContainText('个股风险分析');

    await expect(page.locator('.content-panel')).toHaveScreenshot('risk-management-stock-tab.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 800,
    });
  });

  test('stock tab keeps tablet layout stable', async ({ page }) => {
    await page.setViewportSize({ width: 900, height: 1400 });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page.locator('.artdeco-page-template')).toBeVisible({ timeout: 15000 });
    await page.getByRole('tab', { name: '个股分析' }).click();
    await expect(page.locator('#risk-panel-stock')).toBeVisible();
    await stabilizeVolatileText(page);

    await expect(page.locator('.content-panel')).toHaveScreenshot('risk-management-stock-tablet.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 1200,
    });
  });

  test('overview shell keeps responsive tablet layout stable', async ({ page }) => {
    await page.setViewportSize({ width: 900, height: 1400 });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page.locator('.artdeco-page-template')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#risk-panel-overview')).toBeVisible();
    await stabilizeVolatileText(page);

    await expect(page.locator('.artdeco-page-template')).toHaveScreenshot('risk-management-tablet-overview.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 2500,
    });
  });

  test('overview shell keeps collapsed-sidebar layout stable', async ({ page }) => {
    await page.getByRole('button', { name: 'Toggle sidebar' }).click();
    await page.waitForTimeout(300);
    await stabilizeVolatileText(page);

    await expect(page.locator('.artdeco-page-template')).toHaveScreenshot('risk-management-collapsed-sidebar.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 5000,
    });
  });
});

test.describe('Risk Management Empty State Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await seedVisualSession(page);
    await stubReadiness(page);
    await stubRiskEndpoints(page, {
      payload: emptyPositionsPayload,
      requestId: 'visual-risk-empty',
    });
    await page.goto('/risk-management', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('.artdeco-page-template')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#risk-panel-overview')).toBeVisible();
    await stabilizeVolatileText(page);
    await validateGoldTheme(page);
  });

  test('overview shell keeps empty data layout stable', async ({ page }) => {
    await expect(page.locator('.risk-table')).toBeVisible();
    await expect(page.locator('.risk-table tbody tr')).toHaveCount(0);

    await expect(page.locator('.artdeco-page-template')).toHaveScreenshot('risk-management-empty-overview.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 5000,
    });
  });

  test('empty overview shell keeps collapsed-sidebar layout stable', async ({ page }) => {
    await page.getByRole('button', { name: 'Toggle sidebar' }).click();
    await page.waitForTimeout(300);
    await stabilizeVolatileText(page);

    await expect(page.locator('.artdeco-page-template')).toHaveScreenshot('risk-management-empty-collapsed-sidebar.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 5000,
    });
  });

  test('empty overview shell keeps tablet layout stable', async ({ page }) => {
    await page.setViewportSize({ width: 900, height: 1400 });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page.locator('.artdeco-page-template')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#risk-panel-overview')).toBeVisible();
    await stabilizeVolatileText(page);

    await expect(page.locator('.artdeco-page-template')).toHaveScreenshot('risk-management-empty-tablet-overview.png', {
      animations: 'disabled',
      threshold: 0.2,
      maxDiffPixels: 2500,
    });
  });
});
