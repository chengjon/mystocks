import { test, expect } from '@playwright/test';

test.describe('ArtDeco Dashboard Component Test', () => {
  test('ArtDeco Dashboard should render', async ({ page }) => {
    console.log('Navigating to /dealing-room...');

    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'mock-token-dashboard-test');
      localStorage.setItem('auth_user', JSON.stringify({
        id: 1,
        username: 'admin',
        email: 'admin@mystocks.com',
        role: 'admin',
        permissions: ['*']
      }));
    });

    await page.goto('http://localhost:3020/dealing-room');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    await expect(page).toHaveURL(/\/dealing-room/);

    const app = page.locator('#app');
    await expect(app).toBeVisible();

    const content = await app.innerHTML();
    console.log('Dashboard HTML length:', content.length);

    // Check for ArtDeco components
    const artDecoElements = await page.locator('[class*="artdeco"], [class*="art-deco"]').count();
    console.log('ArtDeco elements found:', artDecoElements);
    expect(artDecoElements).toBeGreaterThan(0);

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
