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
  const palette = await readStablePalette(page, () => {
    const rootStyle = getComputedStyle(document.documentElement);

    return {
      rise: rootStyle.getPropertyValue('--artdeco-rise').trim() || rootStyle.getPropertyValue('--artdeco-up').trim(),
      down: rootStyle.getPropertyValue('--artdeco-down').trim(),
    };
  }, (result) => Boolean(result.rise && result.down));

  expect(palette.rise.toUpperCase()).toBe('#FF5252');
  expect(palette.down.toUpperCase()).toBe('#00E676');
}

export async function validateGoldTheme(page: Page): Promise<void> {
  const palette = await readStablePalette(page, () => {
    const normalizeColor = (value: string): string => {
      const matched = value.match(/\d+/g);
      if (!matched || matched.length < 3) {
        return value.trim().toUpperCase();
      }

      const [red, green, blue] = matched.slice(0, 3).map((part) => Number(part));
      return `#${[red, green, blue].map((part) => part.toString(16).padStart(2, '0')).join('')}`.toUpperCase();
    };

    const rootStyle = getComputedStyle(document.documentElement);
    const goldPrimary = rootStyle.getPropertyValue('--artdeco-gold-primary').trim();
    const goldElement = Array.from(document.querySelectorAll<HTMLElement>('*')).find((element) => {
      const styles = getComputedStyle(element);
      return [
        styles.color,
        styles.borderTopColor,
        styles.borderRightColor,
        styles.borderBottomColor,
        styles.borderLeftColor,
        styles.backgroundColor,
      ]
        .map((value) => normalizeColor(value))
        .includes(goldPrimary.toUpperCase());
    });
    const matchedGoldColor = goldElement
      ? [
          getComputedStyle(goldElement).color,
          getComputedStyle(goldElement).borderTopColor,
          getComputedStyle(goldElement).borderRightColor,
          getComputedStyle(goldElement).borderBottomColor,
          getComputedStyle(goldElement).borderLeftColor,
          getComputedStyle(goldElement).backgroundColor,
        ]
          .map((value) => normalizeColor(value))
          .find((value) => value === goldPrimary.toUpperCase()) || ''
      : '';

    return {
      goldPrimary,
      matchedGoldColor,
    };
  }, (result) => Boolean(result.goldPrimary));

  expect(palette.goldPrimary.toUpperCase()).toBe('#D4AF37');
  if (palette.matchedGoldColor) {
    expect(rgbToHex(palette.matchedGoldColor)).toBe('#D4AF37');
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

async function evaluateWithContextRetry<T>(page: Page, callback: () => T): Promise<T> {
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      await expect(page.locator('body')).toBeVisible({ timeout: 5000 });
      return await page.evaluate(callback);
    } catch (error) {
      if (
        !(error instanceof Error)
        || !error.message.includes('Execution context was destroyed')
      ) {
        throw error;
      }

      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(200);
    }
  }

  return await page.evaluate(callback);
}

async function readStablePalette<T>(
  page: Page,
  callback: () => T,
  isReady: (result: T) => boolean
): Promise<T> {
  let latestResult = await evaluateWithContextRetry(page, callback);

  for (let attempt = 0; attempt < 3; attempt += 1) {
    if (isReady(latestResult)) {
      return latestResult;
    }

    await page.waitForTimeout(300);
    latestResult = await evaluateWithContextRetry(page, callback);
  }

  return latestResult;
}
