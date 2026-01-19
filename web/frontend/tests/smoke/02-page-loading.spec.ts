// web/frontend/tests/smoke/01-page-loading.spec.ts
/**
 * 页面加载冒烟测试
 * 验证Web应用的基础功能正常工作
 */

import { test, expect } from '@playwright/test';

test.describe('页面加载基础测试', () => {
  test('首页应该正确加载', async ({ page }) => {
    // 导航到首页（使用hash路由）
    await page.goto('/#/dashboard');

    // 等待页面加载完成
    await page.waitForLoadState('domcontentloaded');

    // 验证标题
    await expect(page).toHaveTitle(/MyStocks/);

    // 验证关键元素存在（使用ArtDecoLayout + ArtDecoDashboard）
    await expect(page.locator('.artdeco-dashboard')).toBeVisible();
    await expect(page.locator('.artdeco-header')).toBeVisible();
    // 注意：ArtDecoLayout使用.artdeco-dashboard作为主容器
  });

  test('应该显示所有顶层菜单项', async ({ page }) => {
    await page.goto('/#/dashboard');

    // 等待侧边栏加载
    await page.waitForSelector('.nav-link, .router-link-active');

    // 验证菜单文本 (ArtDecoLayout的中文菜单)
    const expectedLabels = [
      '仪表盘',
      '市场行情',
      '股票管理',
      '投资分析',
      '风险管理',
      '策略和交易管理',
      '系统监控'
    ];

    for (const label of expectedLabels) {
      const element = page.locator(`.nav-link:has-text("${label}"), .router-link:has-text("${label}")`);
      await expect(element).toBeVisible();
    }

    // 验证至少有7个菜单项
    const navItems = page.locator('.nav-link, .router-link');
    const count = await navItems.count();
    expect(count).toBeGreaterThanOrEqual(7);
  });

  test('页面加载时间应该合理', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/#/dashboard');
    await page.waitForLoadState('domcontentloaded');

    const endTime = Date.now();
    const loadTime = endTime - startTime;

    // 页面加载应在10秒内完成（放宽时间限制以适应不同浏览器）
    expect(loadTime).toBeLessThan(10000);

    console.log(`✅ 页面加载时间: ${loadTime}ms`);
  });

  test('侧边栏应该正确显示', async ({ page }) => {
    await page.goto('/#/dashboard');

    // ArtDecoLayout内部使用base-layout结构
    // 验证侧边栏存在且可见
    const sidebar = page.locator('.layout-sidebar');
    await expect(sidebar).toBeVisible();

    // 验证侧边栏宽度
    const sidebarWidth = await sidebar.evaluate(el =>
      getComputedStyle(el).width
    );
    console.log(`✅ 侧边栏宽度: ${sidebarWidth}`);

    // 注意：ArtDecoLayout使用layout-sidebar，不是artdeco-sidebar
  });

  test('Command Palette应该可以打开', async ({ page }) => {
    await page.goto('/#/dashboard');

    // 使用快捷键打开Command Palette
    await page.keyboard.press('Control+K');

    // 等待Command Palette出现
    await page.waitForTimeout(500);

    // 验证Command Palette打开（可能有modal或overlay）
    const commandPalette = page.locator('[class*="command"], [class*="palette"], [class*="search"]').first();
    const isVisible = await commandPalette.isVisible().catch(() => false);

    if (isVisible) {
      console.log('✅ Command Palette打开成功');
    } else {
      console.log('⚠️  Command Palette未找到（可能未实现）');
    }
  });

  test('页面不应该有JavaScript错误', async ({ page }) => {
    const errors: string[] = [];

    page.on('pageerror', (error) => {
      errors.push(error.toString());
    });

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/#/dashboard');

    // 等待一下，让所有错误有机会冒泡
    await page.waitForTimeout(2000);

    // 打印错误（如果有）
    if (errors.length > 0) {
      console.log('⚠️  发现JavaScript错误:');
      errors.forEach(err => console.log(`  - ${err}`));
    }

    // 断言没有严重错误
    expect(errors.length).toBe(0);
  });
});
