import { test, expect } from '@playwright/test';

test.describe('Detailed Page Loading Test', () => {
  test('Load dashboard and wait for Vue app', async ({ page }) => {
    // Capture all console messages
    page.on('console', msg => {
      console.log(`[CONSOLE ${msg.type()}]`, msg.text());
      if (msg.type() === 'error') {
        console.error('[ERROR]', msg.text());
      }
    });

    // Capture page errors
    page.on('pageerror', error => {
      console.error('[PAGE ERROR]', error.toString());
    });

    // Navigate to the page
    console.log('[TEST] Navigating to /#/dashboard');
    await page.goto('/#/dashboard');

    // Wait for page load
    console.log('[TEST] Waiting for load state');
    await page.waitForLoadState('domcontentloaded');

    // Wait for Vue app to mount
    console.log('[TEST] Waiting for #app to have content');
    try {
      await page.waitForSelector('#app', { timeout: 5000 });
      console.log('[TEST] #app found');
    } catch (e) {
      console.log('[TEST] #app not found after 5s');
    }

    // Wait and check periodically
    for (let i = 0; i < 10; i++) {
      await page.waitForTimeout(1000);

      const appHTML = await page.locator('#app').innerHTML();
      const htmlLength = appHTML.length;

      console.log(`[TEST] Second ${i + 1}: #app HTML length = ${htmlLength}`);

      if (htmlLength > 3000) {
        console.log('[TEST] App has rendered! Taking screenshot...');
        await page.screenshot({ path: 'test-results/app-rendered.png' });
        break;
      }
    }

    // Final check
    const finalHTML = await page.locator('#app').innerHTML();
    console.log('[TEST] Final HTML length:', finalHTML.length);

    // Try to find any Vue elements
    const vueElements = await page.evaluate(() => {
      const app = document.querySelector('#app');
      if (!app) return { error: 'No #app element' };

      return {
        innerHTML: app.innerHTML.substring(0, 500),
        hasChildren: app.children.length > 0,
        childCount: app.children.length,
        bodyChildren: document.body.children.length
      };
    });

    console.log('[TEST] Vue elements:', vueElements);
  });
});
