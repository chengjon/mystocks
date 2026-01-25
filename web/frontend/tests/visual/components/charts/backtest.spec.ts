import { test, expect } from '../fixtures/visual.fixture';
import { waitForEChartsRender, validateGoldTheme } from '../utils/helpers';

test.describe('Backtest Results Charts - ArtDeco V3.0 Theme', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/backtest', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);
  });

  test('Equity Curve Chart renders correctly', async ({ page }) => {
    const equityChartSelector = '.equity-curve, [class*="equity"]';
    await waitForEChartsRender(page, equityChartSelector);

    await expect(page).toHaveScreenshot('backtest-equity-curve.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('Drawdown Chart displays correctly', async ({ page }) => {
    const drawdownChart = '.drawdown-chart, [class*="drawdown"]';
    await waitForEChartsRender(page, drawdownChart);

    await expect(page).toHaveScreenshot('backtest-drawdown-chart.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('Return Distribution Chart renders correctly', async ({ page }) => {
    const distributionChart = '.return-distribution, [class*="distribution"]';
    await waitForEChartsRender(page, distributionChart);

    await expect(page).toHaveScreenshot('backtest-return-distribution.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('Trades Chart displays entry/exit signals', async ({ page }) => {
    const tradesChart = '.trades-chart, [class*="trades"]';
    await waitForEChartsRender(page, tradesChart);

    await expect(page).toHaveScreenshot('backtest-trades-chart.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('Backtest Results Summary renders with correct metrics', async ({ page }) => {
    const summaryPanel = '.backtest-summary, .results-summary';
    await expect(page.locator(summaryPanel)).toBeVisible({ timeout: 10000 });

    await expect(page).toHaveScreenshot('backtest-summary-panel.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });
});

test.describe('Backtest Results - Strategy Templates', () => {
  test('MA Cross Strategy renders correctly', async ({ page }) => {
    await page.goto('/backtest?strategy=ma_cross', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);

    await waitForEChartsRender(page, '.equity-curve');
    await expect(page).toHaveScreenshot('backtest-ma-cross-strategy.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('RSI Strategy renders correctly', async ({ page }) => {
    await page.goto('/backtest?strategy=rsi', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);

    await waitForEChartsRender(page, '.equity-curve');
    await expect(page).toHaveScreenshot('backtest-rsi-strategy.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('MACD Strategy renders correctly', async ({ page }) => {
    await page.goto('/backtest?strategy=macd', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);

    await waitForEChartsRender(page, '.equity-curve');
    await expect(page).toHaveScreenshot('backtest-macd-strategy.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });

  test('Bollinger Bands Strategy renders correctly', async ({ page }) => {
    await page.goto('/backtest?strategy=bollinger', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);

    await waitForEChartsRender(page, '.equity-curve');
    await expect(page).toHaveScreenshot('backtest-bollinger-strategy.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.25
    });
  });
});
