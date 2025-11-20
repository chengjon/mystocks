import { test, expect } from '@playwright/test';

test('基本测试', async ({ page }) => {
  await page.setContent('<h1>Hello World</h1>');
  
  const h1 = page.locator('h1');
  await expect(h1).toHaveText('Hello World');
  
  console.log('✅ 基本测试通过');
});