import { test, expect } from '@playwright/test';

test.describe('Minimal Suite', () => {
  test('minimal test', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000');
    expect(true).toBe(true);
  });
});
