/**
 * Page Loading Diagnostic Test
 * Check what's actually on the page
 */

import { test, expect } from '@playwright/test';

test.describe('Page Loading Diagnostics', () => {
  test('Check page content', async ({ page }) => {
    await page.goto('/#/dashboard');

    // Wait for page to load
    await page.waitForTimeout(3000);

    // Log page title
    const title = await page.title();
    console.log('Page title:', title);

    // Log page URL
    console.log('Page URL:', page.url());

    // Check for JavaScript errors
    const errors: string[] = [];
    page.on('pageerror', (error) => {
      errors.push(error.toString());
      console.log('JavaScript error:', error.toString());
    });

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.log('Console error:', msg.text());
      }
    });

    // Wait and collect errors
    await page.waitForTimeout(2000);

    // Log all errors found
    console.log('Total errors found:', errors.length);
    errors.forEach(err => console.log('Error:', err));

    // Take screenshot
    await page.screenshot({ path: 'test-results/diagnostic-page.png' });

    // Get page HTML
    const html = await page.content();
    console.log('Page HTML length:', html.length);

    // Check for specific elements
    const selectors = [
      '.base-layout',
      '.layout-sidebar',
      '.nav-item',
      '.sidebar-toggle',
      '#app',
      '.layout-header'
    ];

    for (const selector of selectors) {
      const count = await page.locator(selector).count();
      console.log(`Selector "${selector}": ${count} elements found`);
    }
  });

  test('Check browser console', async ({ page }) => {
    // Collect all console messages
    const messages: string[] = [];

    page.on('console', (msg) => {
      messages.push(`[${msg.type()}] ${msg.text()}`);
    });

    await page.goto('/#/dashboard');
    await page.waitForTimeout(3000);

    console.log('=== Console Messages ===');
    messages.forEach(msg => console.log(msg));
  });
});
