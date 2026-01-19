import { test, expect } from '@playwright/test';

test.describe('Frontend Component Rendering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3020');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);
  });

  test('Vue app mounts successfully', async ({ page }) => {
    const app = page.locator('#app');
    await expect(app).toBeVisible();

    const content = await app.innerHTML();
    console.log('App HTML length:', content.length);
    console.log('App HTML preview:', content.substring(0, 200));
  });

  test('Check for ArtDeco components', async ({ page }) => {
    // Check for ArtDeco-specific classes or elements
    const artDecoElements = await page.locator('[class*="artdeco"], [class*="art-deco"], .art-deco-card, .art-deco-button').count();
    console.log('ArtDeco elements found:', artDecoElements);

    // Check for common component patterns
    const buttons = await page.locator('button').count();
    const cards = await page.locator('[class*="card"]').count();
    const inputs = await page.locator('input').count();

    console.log('UI Elements:', { buttons, cards, inputs });
  });

  test('Check console errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.waitForTimeout(3000);

    console.log('Console errors:', errors);
    console.log('Total errors:', errors.length);
  });

  test('Take screenshot for visual inspection', async ({ page }) => {
    await page.screenshot({
      path: '/tmp/frontend-visual-check.png',
      fullPage: true
    });
    console.log('Screenshot saved to /tmp/frontend-visual-check.png');
  });
});
