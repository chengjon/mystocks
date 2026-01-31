import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const content = await page.evaluate(() => {
      const app = document.querySelector('#app');

      return {
        appHTML: app.innerHTML.substring(0, 500),
        hasRouterView: !!app.querySelector('[class*="router"]'),
        hasArtDecoDashboard: !!app.querySelector('.artdeco-dashboard'),
        hasBaseLayout: !!app.querySelector('.base-layout'),

        // Get page title
        title: document.title
      };
    });

    console.log('[ACTUAL CONTENT]');
    console.log('Title:', content.title);
    console.log('Has router-view:', content.hasRouterView);
    console.log('Has ArtDecoDashboard:', content.hasArtDecoDashboard);
    console.log('Has BaseLayout:', content.hasBaseLayout);
    console.log('');
    console.log('App HTML (first 500 chars):');
    console.log(content.appHTML);

    // Take screenshot
    await page.screenshot({ path: 'current-dashboard-state.png', fullPage: true });
    console.log('[SCREENSHOT] Saved to current-dashboard-state.png');

  } finally {
    await browser.close();
  }
})();
