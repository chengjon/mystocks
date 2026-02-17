import { test, expect } from '@playwright/test';

test('smoke test', async ({ page }) => {
  await page.goto('http://localhost:3020');
  expect(await page.title()).toBeDefined();
});
