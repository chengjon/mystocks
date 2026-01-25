import { test, expect } from '../fixtures/visual.fixture';
import { waitForEChartsRender, validateGoldTheme, validateMarketColors, scrollToChart } from '../utils/helpers';

const ARTDECO_GOLD_PRIMARY = '#D4AF37';
const MARKET_UP = '#FF5252';
const MARKET_DOWN = '#00E676';

test.describe('Dashboard Charts - ArtDeco V3.0 Theme', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    await validateGoldTheme(page);
  });

  test('K-Line Chart renders with ArtDeco theme', async ({ page }) => {
    const chartSelector = '.kline-chart-container, .echarts-container, [class*="k-line"]';
    await waitForEChartsRender(page, chartSelector);

    await expect(page).toHaveScreenshot('dashboard-kline-chart.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('MA Cross Panel displays correctly', async ({ page }) => {
    const panelSelector = '.ma-cross-panel, [class*="ma-cross"]';
    await waitForEChartsRender(page, panelSelector);

    await expect(page).toHaveScreenshot('dashboard-ma-cross-panel.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('RSI Chart renders correctly', async ({ page }) => {
    await page.goto('/technical', { waitUntil: 'networkidle' });
    const rsiSelector = '.rsi-chart, [class*="rsi"]';
    await waitForEChartsRender(page, rsiSelector);

    await expect(page).toHaveScreenshot('dashboard-rsi-chart.png', {
      animations: 'disabled',
      fullPage: false,
      threshold: 0.2
    });
  });

  test('Volume Chart displays with correct market colors', async ({ page }) => {
    await scrollToChart(page, '.volume-chart');
    await waitForEChartsRender(page, '.volume-chart');

    const pageContent = await page.content();
    expect(pageContent).toContain(MARKET_UP);
    expect(pageContent).toContain(MARKET_DOWN);
  });

  test('Dashboard full layout with all charts', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot('dashboard-full-layout.png', {
      animations: 'disabled',
      fullPage: true,
      threshold: 0.25
    });
  });
});

test.describe('ArtDeco Theme Colors', () => {
  test('Gold primary color is applied', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    const pageContent = await page.content();
    expect(pageContent).toContain(ARTDECO_GOLD_PRIMARY);
  });

  test('Market colors (Red/Green) are correct for A股', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    const pageContent = await page.content();
    expect(pageContent).toContain(MARKET_UP);
    expect(pageContent).toContain(MARKET_DOWN);
  });
});
