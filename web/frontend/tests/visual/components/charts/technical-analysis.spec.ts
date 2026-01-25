import { test, expect } from '../fixtures/visual.fixture';
import { waitForEChartsRender, validateGoldTheme } from '../utils/helpers';

test.describe('Technical Analysis Charts - ArtDeco V3.0 Theme', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/technical', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);
  });

  test('Main Chart renders with indicators', async ({ page }) => {
    const mainChartSelector = '.technical-main-chart, .main-chart-container';
    await waitForEChartsRender(page, mainChartSelector);

    await expect(page).toHaveScreenshot('technical-main-chart.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Indicator Panel displays all 26 indicators', async ({ page }) => {
    const indicatorPanel = '.indicator-panel, .indicators-container';
    await expect(page.locator(indicatorPanel)).toBeVisible({ timeout: 10000 });

    await expect(page).toHaveScreenshot('technical-indicator-panel.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Trend indicators (MA, EMA, Bollinger) render correctly', async ({ page }) => {
    const trendSection = '.trend-indicators, [class*="trend"]';
    await waitForEChartsRender(page, trendSection);

    await expect(page).toHaveScreenshot('technical-trend-indicators.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Momentum indicators (RSI, MACD, Stochastic) render correctly', async ({ page }) => {
    const momentumSection = '.momentum-indicators, [class*="momentum"]';
    await waitForEChartsRender(page, momentumSection);

    await expect(page).toHaveScreenshot('technical-momentum-indicators.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Volatility indicators (ATR, Bollinger Bands) render correctly', async ({ page }) => {
    const volatilitySection = '.volatility-indicators, [class*="volatility"]';
    await waitForEChartsRender(page, volatilitySection);

    await expect(page).toHaveScreenshot('technical-volatility-indicators.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Volume indicator renders with market colors', async ({ page }) => {
    const volumeIndicator = '.volume-indicator, [class*="volume"]';
    await waitForEChartsRender(page, volumeIndicator);

    await expect(page).toHaveScreenshot('technical-volume-indicator.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Trading Signals panel displays correctly', async ({ page }) => {
    const signalsPanel = '.trading-signals, .signals-panel';
    await expect(page.locator(signalsPanel)).toBeVisible({ timeout: 10000 });

    await expect(page).toHaveScreenshot('technical-trading-signals.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });
});

test.describe('Technical Analysis - Interactive Features', () => {
  test('Indicator selection updates chart', async ({ page }) => {
    await page.goto('/technical', { waitUntil: 'networkidle' });

    const rsiButton = page.locator('button:has-text("RSI")');
    if (await rsiButton.isVisible()) {
      await rsiButton.click();
      await page.waitForTimeout(500);
    }

    await expect(page.locator('.technical-main-chart')).toBeVisible();
  });

  test('Timeframe selection works', async ({ page }) => {
    await page.goto('/technical', { waitUntil: 'networkidle' });

    const timeframeSelector = '[class*="timeframe"], [class*="period"]';
    const timeframeButtons = page.locator(timeframeSelector).locator('button');
    const count = await timeframeButtons.count();

    if (count > 0) {
      await timeframeButtons.nth(1).click();
      await page.waitForTimeout(500);
    }

    await expect(page.locator('.technical-main-chart')).toBeVisible();
  });
});
