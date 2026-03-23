import { expect, Page } from '@playwright/test';

function rgbToHex(value: string): string {
  const matched = value.match(/\d+/g);
  if (!matched || matched.length < 3) {
    return value.trim().toUpperCase();
  }

  const [red, green, blue] = matched.slice(0, 3).map((part) => Number(part));
  return `#${[red, green, blue].map((part) => part.toString(16).padStart(2, '0')).join('')}`.toUpperCase();
}

export async function waitForEChartsRender(page: Page, containerSelector: string): Promise<void> {
  await page.waitForSelector(`${containerSelector} canvas`, { timeout: 10000 });
  await page.waitForTimeout(1500);
}

export async function getChartContainerSize(page: Page, containerSelector: string): Promise<{ width: number; height: number }> {
  const container = page.locator(containerSelector);
  const box = await container.boundingBox();
  return { width: box?.width || 0, height: box?.height || 0 };
}

export async function validateMarketColors(page: Page): Promise<void> {
  const palette = await page.evaluate(() => {
    const rootStyle = getComputedStyle(document.documentElement);

    return {
      rise: rootStyle.getPropertyValue('--artdeco-rise').trim() || rootStyle.getPropertyValue('--artdeco-up').trim(),
      down: rootStyle.getPropertyValue('--artdeco-down').trim(),
    };
  });

  expect(palette.rise.toUpperCase()).toBe('#FF5252');
  expect(palette.down.toUpperCase()).toBe('#00E676');
}

export async function validateGoldTheme(page: Page): Promise<void> {
  const palette = await page.evaluate(() => {
    const rootStyle = getComputedStyle(document.documentElement);
    const goldElement = document.querySelector('.brand-text, .divider-text, .nav-icon, .domain-label');
    return {
      goldPrimary: rootStyle.getPropertyValue('--artdeco-gold-primary').trim(),
      goldElementColor: goldElement ? getComputedStyle(goldElement).color : '',
    };
  });

  expect(palette.goldPrimary.toUpperCase()).toBe('#D4AF37');
  expect(rgbToHex(palette.goldElementColor)).toBe('#D4AF37');
}

export function generateChartTestName(chartType: string, variant: string): string {
  return `artdeco-${chartType}-${variant}`.toLowerCase().replace(/\s+/g, '-');
}

export async function scrollToChart(page: Page, selector: string): Promise<void> {
  const element = page.locator(selector);
  await element.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
}

export async function dismissOverlay(page: Page): Promise<void> {
  const closeButtons = page.locator('button:has-text("Close"), button:has-text("×"), .el-popper__close-btn');
  if (await closeButtons.first().isVisible()) {
    await closeButtons.first().click();
    await page.waitForTimeout(300);
  }
}
