import { test, expect } from '@playwright/test';

test.describe('超简单测试', () => {
  test('基础测试1', async ({ page }) => {
    await page.setContent('<h1>Hello World</h1>');
    
    const h1 = page.locator('h1');
    await expect(h1).toHaveText('Hello World');
    
    console.log('✅ 基础测试1通过');
  });

  test('基础测试2', async ({ page }) => {
    await page.setContent('<div id="test">Test Content</div>');
    
    const div = page.locator('#test');
    await expect(div).toHaveText('Test Content');
    
    console.log('✅ 基础测试2通过');
  });
});