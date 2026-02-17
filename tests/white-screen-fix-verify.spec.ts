import { test, expect } from '@playwright/test';

test('White Screen Fix Verification', async ({ page }) => {
  // 设置超时
  test.setTimeout(60000);
  
  console.log('Navigating to http://localhost:3000...');
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
  
  // 截图留证
  await page.screenshot({ path: 'test-results/white-screen-check.png' });
  
  // 检查 Vue 挂载
  const childrenCount = await page.evaluate(() => document.getElementById('app')?.children.length || 0);
  console.log(`App children count: ${childrenCount}`);
  
  expect(childrenCount).toBeGreaterThan(0);
  
  // 检查关键字
  const title = await page.title();
  console.log(`Page title: ${title}`);
  expect(title).toContain('MyStocks');
});
