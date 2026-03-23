import { expect, test } from '../../fixtures/visual.fixture';
import { validateGoldTheme } from '../../utils/helpers';

const VISUAL_USER = {
  id: 1,
  username: 'visual-admin',
  email: 'visual-admin@example.com',
  role: 'admin',
  permissions: ['*'],
};

const STRATEGY_LIST_ENDPOINTS = [
  '**/api/v1/strategy/strategies**',
  '**/api/mock/strategy/strategies**',
  '**/api/api/v1/strategy/strategies**',
  '**/api/api/mock/strategy/strategies**',
];

async function seedVisualSession(page: Parameters<typeof test>[0]['page']) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await page.evaluate((user) => {
    localStorage.setItem('auth_token', 'visual-backtest-token');
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

async function stubStrategyEndpoints(page: Parameters<typeof test>[0]['page']) {
  await page.route('**/api/csrf-token', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: { csrf_token: 'visual-backtest-csrf' },
      }),
    });
  });

  for (const endpoint of STRATEGY_LIST_ENDPOINTS) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          code: 200,
          message: 'ok',
          data: [
            {
              strategy_id: 101,
              strategy_name: 'Momentum Alpha',
              strategy_type: 'momentum',
              status: 'active',
              description: 'alpha',
              updated_at: '2026-03-01T09:00:00Z',
            },
            {
              strategy_id: 102,
              strategy_name: 'Mean Reversion Beta',
              strategy_type: 'mean_reversion',
              status: 'paused',
              description: 'beta',
              updated_at: '2026-03-01T09:05:00Z',
            },
          ],
          request_id: 'visual-backtest-list',
        }),
      });
    });
  }
}

test.describe('Backtest Visual Charts', () => {
  test.beforeEach(async ({ page }) => {
    await seedVisualSession(page);
    await stubReadiness(page);
    await stubStrategyEndpoints(page);
    await page.goto('/strategy/backtest', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
    await validateGoldTheme(page);
  });

  test('execution hub keeps progress and logs readable', async ({ page }) => {
    await expect(page.getByRole('heading', { name: '策略回测管理中心' })).toBeVisible();
    await expect(page.locator('.progress-panel')).toBeVisible();
    await expect(page.locator('.log-panel')).toBeVisible();

    await expect(page.locator('.hub-grid')).toHaveScreenshot('backtest-execution-hub.png', {
      animations: 'disabled',
      threshold: 0.2,
    });
  });

  test('report tab keeps summary layout stable', async ({ page }) => {
    await page.getByRole('button', { name: '报告中心' }).click();
    await expect(page.locator('.tab-panel')).toContainText('回测报告');

    await expect(page.locator('.tab-panel')).toHaveScreenshot('backtest-report-tab.png', {
      animations: 'disabled',
      threshold: 0.2,
    });
  });
});
