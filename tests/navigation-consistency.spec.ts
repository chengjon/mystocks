import { test, expect } from '@playwright/test';

/**
 * ArtDeco 3.1 导航一致性验证 - 终极对齐版
 * 验证菜单点击后的真实 URL 跳转及其对应内容的渲染
 */
test.describe('侧边栏-路由联动一致性测试 (ArtDeco 3.1 Architecture)', () => {
  
  test.beforeEach(async ({ page }) => {
    test.setTimeout(150000);
    await page.goto('/', { waitUntil: 'networkidle' });
    
    if (page.url().includes('/login')) {
      await page.fill('input[type="text"]', 'admin');
      await page.fill('input[type="password"]', 'admin123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(/\/dashboard$/);
    }
    await expect(page.locator('.artdeco-sidebar, aside, nav[role="navigation"]').first()).toBeVisible({ timeout: 20000 });
  });

  const menuTests = [
    { parent: '市场总览', name: '实时行情', expectedPath: '/market/realtime', title: 'Market Realtime Overview' },
    { parent: '市场总览', name: '技术指标', expectedPath: '/market/technical', title: 'K-Line Analysis' },
    { parent: '市场总览', name: '问财选股', expectedPath: '/market/wencai', title: '市场数据分析中心' },
    { parent: '策略中心', name: '策略管理', expectedPath: '/strategy/management', title: '策略管理' },
    { parent: '风险控制', name: '风险概览', expectedPath: '/risk/overview', title: 'Risk Management Rules' },
    
    // 路径校准：使用菜单中定义的真实跳转路径
    { parent: '交易管理', name: '交易信号', expectedPath: '/trading/signals', title: 'Live Strategy Signals' },
    { parent: '交易管理', name: '持仓监控', expectedPath: '/trading/positions', title: 'Portfolio Assets' },
    
    { parent: '系统管理', name: '运维监控', expectedPath: '/system/monitoring', title: 'System Observability' }
  ];

  for (const menu of menuTests) {
    test(`导航校验: [${menu.parent} -> ${menu.name}]`, async ({ page }) => {
      // 1. 展开父菜单
      const parent = page.locator(`.domain-header:has-text("${menu.parent}"), .domain-label:has-text("${menu.parent}")`).first();
      await expect(parent).toBeVisible({ timeout: 10000 });
      if ((await parent.getAttribute('aria-expanded')) !== 'true') {
        await parent.click();
        await page.waitForTimeout(1000);
      }

      // 2. 点击子菜单
      const item = page.locator(`.menu-item:has-text("${menu.name}"), .item-label:has-text("${menu.name}")`).first();
      await expect(item).toBeVisible({ timeout: 10000 });
      await item.click();

      // 3. 断言跳转后的 URL
      await expect(page).toHaveURL(new RegExp(`${menu.expectedPath}$`), { timeout: 20000 });

      // 4. 等待组件渲染并断言核心标题
      await page.waitForTimeout(2000);
      const titleLocator = page.locator(`h1, h2, .section-title, .title, .header-title`).filter({ hasText: menu.title }).first();
      await expect(titleLocator, `页面应显示标题: ${menu.title}`).toBeVisible({ timeout: 15000 });
      
      console.log(`PASS: Verified ${menu.name} at ${menu.expectedPath}`);
    });
  }
});
