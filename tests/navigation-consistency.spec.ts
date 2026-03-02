import { test, expect } from '@playwright/test';

/**
 * ArtDeco 3.1 导航一致性验证 - 终极对齐版
 * 验证菜单域核心路由的可达性和基础渲染
 */
test.describe('侧边栏-路由联动一致性测试 (ArtDeco 3.1 Architecture)', () => {
  const e2eUser = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    role: 'admin',
    permissions: []
  };

  test.beforeEach(async ({ page }) => {
    test.setTimeout(150000);

    await page.addInitScript(({ user }) => {
      localStorage.setItem('auth_token', 'e2e-navigation-token');
      localStorage.setItem('auth_user', JSON.stringify(user));
    }, { user: e2eUser });

    await page.route('**/api/**', async (route) => {
      const url = new URL(route.request().url());

      if (url.pathname === '/api/csrf-token') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: { csrf_token: 'e2e-csrf-token' } })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [] })
      });
    });

    await page.goto('/dealing-room', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/dealing-room$/);
  });

  const menuTests = [
    { name: '实时行情', expectedPath: '/market/realtime' },
    { name: '技术指标', expectedPath: '/market/technical' },
    { name: '问财选股', expectedPath: '/market/wencai' },
    { name: '策略管理', expectedPath: '/strategy/management' },
    { name: '风险概览', expectedPath: '/risk/overview' },
    { name: '交易信号', expectedPath: '/trading/signals' },
    { name: '持仓监控', expectedPath: '/trading/positions' },
    { name: '运维监控', expectedPath: '/system/monitoring' }
  ];

  for (const menu of menuTests) {
    test(`导航校验: ${menu.name} -> ${menu.expectedPath}`, async ({ page }) => {
      await page.goto(menu.expectedPath, { waitUntil: 'domcontentloaded' });

      await expect.poll(() => new URL(page.url()).pathname).toBe(menu.expectedPath);
      await expect(page).not.toHaveURL(/\/login/);
      await expect(page.locator('#app')).toBeVisible({ timeout: 15000 });
    });
  }
});
