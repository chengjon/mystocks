import { test, expect } from '@playwright/test';

test('Chrome DevTools simple test', async ({ page }) => {
  console.log('Starting Chrome DevTools test...');
  
  // Test with a known website first
  await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });
  
  // Wait for page to load
  await page.waitForTimeout(3000);
  
  // Check page title
  const title = await page.title();
  console.log(`Page title: ${title}`);
  expect(title).toContain('Example');
  
  // Take a screenshot
  await page.screenshot({ 
    path: 'test-results/example-page.png', 
    fullPage: true 
  });
  
  console.log('Basic Chrome DevTools test completed successfully!');
});