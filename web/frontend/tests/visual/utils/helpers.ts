import { Page } from '@playwright/test';

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
  const upColor = '#FF5252';
  const downColor = '#00E676';
  const pageContent = await page.content();
  expect(pageContent).toContain(upColor);
  expect(pageContent).toContain(downColor);
}

export async function validateGoldTheme(page: Page): Promise<void> {
  const goldColors = ['#D4AF37', '#F0E68C', '#CD7F32', '#F7E7CE'];
  const pageContent = await page.content();
  for (const color of goldColors) {
    expect(pageContent).toContain(color);
  }
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
