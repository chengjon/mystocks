import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Capture console messages
  page.on('console', msg => {
    console.log(`[CONSOLE ${msg.type()}]`, msg.text());
  });

  // Capture page errors
  page.on('pageerror', error => {
    console.error('[PAGE ERROR]', error.message);
    console.error(error.stack);
  });

  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);

    // Check if Vue app exists
    const hasVue = await page.evaluate(() => {
      return typeof window.$vue !== 'undefined';
    });
    console.log('[CHECK] window.$vue exists:', hasVue);

    // Check #app content
    const appHTML = await page.locator('#app').innerHTML();
    console.log('[CHECK] #app HTML length:', appHTML.length);
    console.log('[CHECK] #app content:', appHTML.substring(0, 100));

    // Check for Vue instance
    const vueInstance = await page.evaluate(() => {
      const app = document.querySelector('#app');
      return app ? app.__vue_app__ : null;
    });
    console.log('[CHECK] Vue instance on #app:', vueInstance ? 'YES' : 'NO');

  } catch (error) {
    console.error('[TEST ERROR]', error);
  } finally {
    await browser.close();
  }
})();
