import { test, expect } from '@playwright/test';

test('Dashboard Hidden Access Verification', async ({ page }) => {
  // 1. 访问根路径，应重定向到 /dashboard
  console.log('Navigating to root...');
  await page.goto('/', { waitUntil: 'networkidle' });
  
  const currentUrl = page.url();
  console.log(`Redirected to: ${currentUrl}`);
  expect(currentUrl).toContain('/dashboard');
  
  // 2. 检查侧边栏菜单项
  // 获取所有一级菜单的文本
  const menuItems = await page.locator('.artdeco-menu-item .menu-label').allTextContents();
  console.log('Menu Items found:', menuItems);
  
  // 断言：菜单中不应包含 "指挥中心"
  const hasDashboardInMenu = menuItems.some(item => item.includes('指挥中心'));
  expect(hasDashboardInMenu).toBe(false);
  
  // 断言：应包含 "市场总览"
  expect(menuItems).toContain('市场总览');
});
