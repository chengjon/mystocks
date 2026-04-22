import { expect, test } from '../../fixtures/visual.fixture';
import { validateGoldTheme } from '../../utils/helpers';

test.use({ serviceWorkers: 'block' });

const VISUAL_USER = {
  id: 1,
  username: 'visual-admin',
  email: 'visual-admin@example.com',
  role: 'admin',
  permissions: ['*'],
};

const MOCK_KLINE = [
  { datetime: '2026-03-01 15:00:00', open: 100, high: 102, low: 99, close: 101, volume: 1000000 },
  { datetime: '2026-03-02 15:00:00', open: 101, high: 103, low: 100, close: 102, volume: 1100000 },
  { datetime: '2026-03-03 15:00:00', open: 102, high: 104, low: 101, close: 103, volume: 1200000 },
];

async function seedVisualSession(page: Parameters<typeof test>[0]['page']) {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await page.evaluate((user) => {
    localStorage.setItem('auth_token', 'visual-technical-token');
    localStorage.setItem('token', 'visual-technical-token');
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('user', JSON.stringify(user));
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

async function stubKline(page: Parameters<typeof test>[0]['page']) {
  await page.route('**/api/v1/market/kline**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: { data: MOCK_KLINE },
        request_id: 'visual-kline',
      }),
    });
  });
}

test.describe('Technical Analysis Visual Charts', () => {
  test.beforeEach(async ({ page }) => {
    await seedVisualSession(page);
    await stubReadiness(page);
    await stubKline(page);
    await page.goto('/market/technical', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1200);
    await validateGoldTheme(page);
  });

  test('kline hero panel remains visually stable', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'K-Line Analysis' })).toBeVisible();
    await expect(page.locator('.kline-container')).toBeVisible();

    await expect(page.locator('.kline-container')).toHaveScreenshot('technical-kline-container.png', {
      animations: 'disabled',
      threshold: 0.2,
    });
  });

  test('kline data table remains visually stable', async ({ page }) => {
    await expect(page.locator('.data-table-section')).toContainText('DATE');

    await expect(page.locator('.data-table-section')).toHaveScreenshot('technical-kline-table.png', {
      animations: 'disabled',
      threshold: 0.2,
    });
  });
});
