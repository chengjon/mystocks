import { test as base, expect, Page } from '@playwright/test';

interface VisualFixtures {
  chartLocator: (selector: string) => Promise<void>;
  waitForChartRender: (selector: string) => Promise<void>;
  takeChartScreenshot: (name: string) => Promise<void>;
  validateArtDecoColors: () => Promise<void>;
}

export const test = base.extend<VisualFixtures>({
  chartLocator: async ({ page }, use) => {
    await use(async (selector: string) => {
      const chart = page.locator(selector);
      await expect(chart).toBeVisible({ timeout: 10000 });
      await chart.waitFor({ state: 'attached' });
    });
  },
  waitForChartRender: async ({ page }, use) => {
    await use(async (selector: string) => {
      await page.waitForSelector(`${selector} canvas`, { timeout: 10000 });
      await page.waitForTimeout(1000);
    });
  },
  takeChartScreenshot: async ({ page }, use) => {
    await use(async (name: string) => {
      await expect(page).toHaveScreenshot(`${name}.png`, {
        animations: 'disabled',
        fullPage: false
      });
    });
  },
  validateArtDecoColors: async ({ page }, use) => {
    await use(async () => {
      const goldColors = ['#D4AF37', '#F0E68C', '#CD7F32', '#F7E7CE'];
      const pageContent = await page.content();
      for (const color of goldColors) {
        expect(pageContent).toContain(color);
      }
    });
  }
});

export { expect };
