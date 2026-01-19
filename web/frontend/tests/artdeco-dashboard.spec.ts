import { test, expect } from '@playwright/test';

test.describe('ArtDeco Dashboard Component Test', () => {
  test('ArtDeco Dashboard should render', async ({ page }) => {
    console.log('Navigating to /dashboard...');
    await page.goto('http://localhost:3020/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    const app = page.locator('#app');
    await expect(app).toBeVisible();

    const content = await app.innerHTML();
    console.log('Dashboard HTML length:', content.length);

    // Check for ArtDeco components
    const artDecoElements = await page.locator('[class*="artdeco"], [class*="art-deco"]').count();
    console.log('ArtDeco elements found:', artDecoElements);

    // Check for specific ArtDeco components
    const statCards = await page.locator('[class*="stat-card"]').count();
    const topBars = await page.locator('[class*="top-bar"]').count();
    const cards = await page.locator('[class*="card"]').count();

    console.log('ArtDeco Components:', { statCards, topBars, cards });

    // Take screenshot
    await page.screenshot({
      path: '/tmp/artdeco-dashboard.png',
      fullPage: true
    });
    console.log('Screenshot saved to /tmp/artdeco-dashboard.png');

    // Check console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.waitForTimeout(2000);
    console.log('Console errors:', errors);
  });
});
