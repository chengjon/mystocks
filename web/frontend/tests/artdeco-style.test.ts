import { expect, test } from '@playwright/test';

test.describe('ArtDeco Style Gate', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('loads core ArtDeco CSS variables globally', async ({ page }) => {
    const tokens = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      return {
        accent: styles.getPropertyValue('--color-accent').trim(),
        artdecoGold: styles.getPropertyValue('--artdeco-gold-primary').trim(),
        textPrimary: styles.getPropertyValue('--color-text-primary').trim(),
      };
    });

    expect(tokens.accent).not.toBe('');
    expect(tokens.artdecoGold).not.toBe('');
    expect(tokens.textPrimary).not.toBe('');
  });

  test('keeps the active shell on desktop layout primitives', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await expect(page.locator('#app')).toBeVisible();
    await expect(page.locator('body')).toBeVisible();
    await expect(page.getByText(/System Readiness|登录|Dashboard|正在检查后端就绪状态/).first()).toBeVisible();
  });

  test('does not expose mobile navigation affordances', async ({ page }) => {
    await expect(page.locator('[aria-label*="mobile" i]')).toHaveCount(0);
    await expect(page.locator('[class*="hamburger" i]')).toHaveCount(0);
  });
});
