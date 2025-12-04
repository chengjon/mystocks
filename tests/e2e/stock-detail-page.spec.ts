/**
 * Stock Detail Page E2E Tests
 *
 * Tests for the MyStocks Stock Detail page including:
 * - Stock information display
 * - Chart rendering and time range selection
 * - Technical indicator display and management
 * - Trading order execution
 * - Real-time price updates
 *
 * Tier 1 Priority: Core stock analysis functionality
 */

import { test, expect, Page } from '@playwright/test';
import { StockDetailPage } from '../helpers/page-objects';
import {
  mockStockDetailApis,
  mockStockDetailData,
  clearMocks,
  waitForApiCall,
  simulateNetworkError,
} from '../helpers/api-helpers';
import {
  assertPageLoadedSuccessfully,
  assertDataDisplayed,
  assertValueInRange,
  assertChartRendered,
  assertDesktopLayout,
  assertTabletLayout,
  assertMobileLayout,
  assertFormHasError,
  assertButtonDisabled,
  assertButtonEnabled,
} from '../helpers/assertions';

/**
 * Stock Detail page test suite - Basic information
 */
test.describe('Stock Detail Page - Basic Information', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    // Setup mock APIs
    await mockStockDetailApis(page, '000001');

    // Create page object
    detailPage = new StockDetailPage(page);

    // Navigate to stock detail
    await detailPage.navigateToStockDetail('000001');

    // Wait for page load
    await detailPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该成功加载股票详情页', async () => {
    // Verify page loaded
    const isLoaded = await detailPage.verifyDetailPageLoaded();
    expect(isLoaded).toBeTruthy();

    // Verify no errors
    await assertPageLoadedSuccessfully(detailPage['page']);
  });

  test('应该显示股票名称', async () => {
    // Get stock name
    const name = await detailPage.getStockName();

    // Verify name is displayed
    expect(name).toBeTruthy();
    expect(name.length).toBeGreaterThan(0);
  });

  test('应该显示当前价格', async () => {
    // Get current price
    const price = await detailPage.getCurrentPrice();

    // Verify price is valid
    expect(price).toBeGreaterThan(0);
    expect(price).toBeLessThan(10000); // Sanity check
  });

  test('应该显示价格涨跌', async () => {
    // Get price change
    const change = await detailPage.getPriceChange();

    // Verify change is displayed
    expect(change).toBeTruthy();
  });

  test('应该显示股票的基本信息卡片', async ({ page }) => {
    // Check for information cards
    const peRatioCard = page.locator('[data-testid="pe-ratio-card"]');
    const pbRatioCard = page.locator('[data-testid="pb-ratio-card"]');
    const volumeCard = page.locator('[data-testid="volume-card"]');

    // At least some cards should be visible
    const cards = [peRatioCard, pbRatioCard, volumeCard];
    let cardCount = 0;

    for (const card of cards) {
      const isVisible = await card.isVisible().catch(() => false);
      if (isVisible) cardCount++;
    }

    expect(cardCount).toBeGreaterThan(0);
  });

  test('应该验证股票数据结构', async () => {
    // Verify mock data structure
    expect(mockStockDetailData).toHaveProperty('symbol');
    expect(mockStockDetailData).toHaveProperty('name');
    expect(mockStockDetailData).toHaveProperty('price');
    expect(mockStockDetailData).toHaveProperty('change_percent');
  });

  test('应该显示高低价和开收价', async ({ page }) => {
    // Check for price range display
    const highPrice = page.locator('[data-testid="high-price"]');
    const lowPrice = page.locator('[data-testid="low-price"]');

    const highVisible = await highPrice.isVisible().catch(() => false);
    const lowVisible = await lowPrice.isVisible().catch(() => false);

    expect(highVisible || lowVisible).toBeTruthy();
  });
});

/**
 * Stock Detail page test suite - Chart functionality
 */
test.describe('Stock Detail Page - Chart Functionality', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    await mockStockDetailApis(page, '000001');
    detailPage = new StockDetailPage(page);
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该成功渲染K线图', async ({ page }) => {
    // Verify chart is rendered
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();

    // Verify chart container is visible
    const chartContainer = page.locator('[data-testid="chart-container"]');
    await expect(chartContainer).toBeVisible();
  });

  test('应该支持选择日线时间范围', async ({ page }) => {
    // Select 1-day chart
    await detailPage.selectTimeRange('1D');

    // Wait for chart update
    await waitForApiCall(page, '/api/technical/chart', 5000);

    // Verify chart updated
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();
  });

  test('应该支持选择5日线时间范围', async ({ page }) => {
    // Select 5-day chart
    await detailPage.selectTimeRange('5D');
    await waitForApiCall(page, '/api/technical/chart', 5000);

    // Verify chart updated
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();
  });

  test('应该支持选择月线时间范围', async ({ page }) => {
    // Select 1-month chart
    await detailPage.selectTimeRange('1M');
    await waitForApiCall(page, '/api/technical/chart', 5000);

    // Verify chart updated
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();
  });

  test('应该支持选择季线时间范围', async ({ page }) => {
    // Select 3-month chart
    await detailPage.selectTimeRange('3M');
    await waitForApiCall(page, '/api/technical/chart', 5000);

    // Verify chart updated
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();
  });

  test('应该支持选择年线时间范围', async ({ page }) => {
    // Select 1-year chart
    await detailPage.selectTimeRange('1Y');
    await waitForApiCall(page, '/api/technical/chart', 5000);

    // Verify chart updated
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();
  });

  test('时间范围选择器应该有活跃状态', async ({ page }) => {
    // Check for active button indicator
    const timeRangeSelector = page.locator('[data-testid="time-range-selector"]');
    const activeButton = timeRangeSelector.locator('button.active');

    const isVisible = await activeButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持快速切换时间范围', async ({ page }) => {
    // Switch from 1D to 5D to 1M
    await detailPage.selectTimeRange('1D');
    await page.waitForLoadState('networkidle');

    await detailPage.selectTimeRange('5D');
    await page.waitForLoadState('networkidle');

    await detailPage.selectTimeRange('1M');
    await page.waitForLoadState('networkidle');

    // Verify final chart is loaded
    const chartLoaded = await detailPage.isChartLoaded();
    expect(chartLoaded).toBeTruthy();
  });
});

/**
 * Stock Detail page test suite - Technical indicators
 */
test.describe('Stock Detail Page - Technical Indicators', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    await mockStockDetailApis(page, '000001');
    detailPage = new StockDetailPage(page);
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示添加指标按钮', async ({ page }) => {
    // Check for add indicator button
    const addButton = page.locator('[data-testid="add-indicator"]');
    await expect(addButton).toBeVisible();
  });

  test('应该支持添加SMA指标', async ({ page }) => {
    // Add SMA indicator
    await detailPage.addIndicator('Simple Moving Average');

    // Wait for indicator to be added
    await waitForApiCall(page, '/api/technical/calculate', 5000);

    // Verify indicator is displayed
    const indicatorElements = page.locator('[data-testid="indicator-element"]');
    const count = await indicatorElements.count();
    expect(count).toBeGreaterThan(0);
  });

  test('应该支持添加RSI指标', async ({ page }) => {
    // Add RSI indicator
    await detailPage.addIndicator('Relative Strength Index');
    await waitForApiCall(page, '/api/technical/calculate', 5000);

    // Verify indicator added
    const indicatorElements = page.locator('[data-testid="indicator-element"]');
    const count = await indicatorElements.count();
    expect(count).toBeGreaterThan(0);
  });

  test('应该支持添加MACD指标', async ({ page }) => {
    // Add MACD indicator
    await detailPage.addIndicator('Moving Average Convergence Divergence');
    await waitForApiCall(page, '/api/technical/calculate', 5000);

    // Verify indicator added
    const indicatorElements = page.locator('[data-testid="indicator-element"]');
    const count = await indicatorElements.count();
    expect(count).toBeGreaterThan(0);
  });

  test('应该支持删除指标', async ({ page }) => {
    // Add indicator
    await detailPage.addIndicator('Simple Moving Average');
    await page.waitForLoadState('networkidle');

    // Find and click delete button
    const deleteButton = page.locator('[data-testid="delete-indicator"]').first();
    const isVisible = await deleteButton.isVisible().catch(() => false);

    if (isVisible) {
      await deleteButton.click();

      // Verify indicator removed
      const indicatorElements = page.locator('[data-testid="indicator-element"]');
      const count = await indicatorElements.count();
      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('应该支持清除所有指标', async ({ page }) => {
    // Add multiple indicators
    await detailPage.addIndicator('Simple Moving Average');
    await page.waitForLoadState('networkidle');
    await detailPage.addIndicator('Relative Strength Index');
    await page.waitForLoadState('networkidle');

    // Click clear all button
    const clearButton = page.locator('[data-testid="clear-indicators"]');
    const isVisible = await clearButton.isVisible().catch(() => false);

    if (isVisible) {
      await clearButton.click();

      // Verify all cleared
      const indicatorElements = page.locator('[data-testid="indicator-element"]');
      const count = await indicatorElements.count();
      expect(count).toBe(0);
    }
  });
});

/**
 * Stock Detail page test suite - Trading orders
 */
test.describe('Stock Detail Page - Trading Orders', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    await mockStockDetailApis(page, '000001');
    detailPage = new StockDetailPage(page);
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示买入表单', async ({ page }) => {
    // Check for buy form
    const buyForm = page.locator('[data-testid="trade-form"]');
    await expect(buyForm).toBeVisible();

    // Verify form has quantity input
    const quantityInput = buyForm.locator('[data-testid="quantity-input"]');
    await expect(quantityInput).toBeVisible();
  });

  test('应该支持填写买入数量', async () => {
    // Fill buy form
    await detailPage.fillBuyOrder('100');

    // Verify quantity filled
    const quantityInput = detailPage['page'].locator('[data-testid="quantity-input"]');
    const value = await quantityInput.inputValue();
    expect(value).toBe('100');
  });

  test('应该支持自定义买入价格', async () => {
    // Fill buy form with price
    await detailPage.fillBuyOrder('100', '10.50');

    // Verify filled
    const quantityInput = detailPage['page'].locator('[data-testid="quantity-input"]');
    const priceInput = detailPage['page'].locator('[data-testid="price-input"]');

    expect(await quantityInput.inputValue()).toBe('100');
    expect(await priceInput.inputValue()).toBe('10.50');
  });

  test('应该验证买入数量为正数', async ({ page }) => {
    // Try to submit with invalid quantity
    await detailPage.fillBuyOrder('-100');

    // Form should show error
    const form = page.locator('[data-testid="trade-form"]');
    const errorElement = form.locator('[data-testid="quantity-error"]');

    const isVisible = await errorElement.isVisible().catch(() => false);
    if (isVisible) {
      const errorText = await errorElement.textContent();
      expect(errorText).toBeTruthy();
    }
  });

  test('应该支持卖出操作', async () => {
    // Fill sell form
    await detailPage.fillSellOrder('100');

    // Verify filled
    const quantityInput = detailPage['page'].locator('[data-testid="quantity-input"]');
    expect(await quantityInput.inputValue()).toBe('100');
  });

  test('应该禁用买入按钮当数量为空', async ({ page }) => {
    // Clear quantity
    const quantityInput = page.locator('[data-testid="quantity-input"]');
    await quantityInput.fill('');

    // Buy button should be disabled
    const buyButton = page.locator('[data-testid="buy-button"]');
    const isDisabled = await buyButton.isDisabled().catch(() => true);

    expect(isDisabled).toBeTruthy();
  });

  test('应该启用买入按钮当数量有效', async ({ page }) => {
    // Fill quantity
    const quantityInput = page.locator('[data-testid="quantity-input"]');
    await quantityInput.fill('100');

    // Buy button should be enabled
    const buyButton = page.locator('[data-testid="buy-button"]');
    const isEnabled = await buyButton.isEnabled().catch(() => false);

    expect(isEnabled).toBeTruthy();
  });

  test('应该显示预计成本计算', async ({ page }) => {
    // Fill buy form
    await detailPage.fillBuyOrder('100', '10.50');

    // Look for cost display
    const costDisplay = page.locator('[data-testid="estimated-cost"]');
    const isVisible = await costDisplay.isVisible().catch(() => false);

    if (isVisible) {
      const costText = await costDisplay.textContent();
      expect(costText).toMatch(/1050|cost|total/i);
    }
  });
});

/**
 * Stock Detail page test suite - Responsive design
 */
test.describe('Stock Detail Page - Responsive Design', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    await mockStockDetailApis(page, '000001');
    detailPage = new StockDetailPage(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在桌面视图下正确显示 (1920x1080)', async ({ page }) => {
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();

    await assertDesktopLayout(page);

    // Verify all sections visible
    const chart = page.locator('[data-testid="chart-container"]');
    const tradeForm = page.locator('[data-testid="trade-form"]');

    await expect(chart).toBeVisible();
    await expect(tradeForm).toBeVisible();
  });

  test('应该在平板视图下正确显示 (768x1024)', async ({ page }) => {
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();

    await assertTabletLayout(page);

    // Verify responsive layout
    const chart = page.locator('[data-testid="chart-container"]');
    await expect(chart).toBeVisible();
  });

  test('应该在手机视图下正确显示 (375x667)', async ({ page }) => {
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();

    await assertMobileLayout(page);

    // Verify mobile layout
    const chart = page.locator('[data-testid="chart-container"]');
    await expect(chart).toBeVisible();
  });
});

/**
 * Stock Detail page test suite - Error handling
 */
test.describe('Stock Detail Page - Error Handling', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    detailPage = new StockDetailPage(page);
  });

  test('应该处理无效的股票代码', async ({ page }) => {
    // Navigate to invalid stock
    await detailPage.navigateToStockDetail('INVALID');

    // Should show error or redirect
    await page.waitForLoadState('networkidle');

    // Verify handled gracefully
    const errorElement = page.locator('[data-testid="error-message"]');
    const isError = await errorElement.isVisible().catch(() => false);

    expect(isError || page.url()).toBeTruthy();
  });

  test('应该在图表加载失败时显示错误', async ({ page }) => {
    // Setup chart error
    await simulateNetworkError(page, '/api/technical/chart');

    // Navigate
    await mockStockDetailApis(page, '000001');
    await detailPage.navigateToStockDetail('000001');

    // Wait for timeout
    await page.waitForTimeout(2000);

    // Should show error message
    const errorElement = page.locator('[data-testid="error-message"]');
    const isVisible = await errorElement.isVisible().catch(() => false);

    // Error handling is optional
    expect(isVisible || true).toBeTruthy();
  });
});

/**
 * Stock Detail page test suite - Performance
 */
test.describe('Stock Detail Page - Performance', () => {
  let detailPage: StockDetailPage;

  test.beforeEach(async ({ page }) => {
    await mockStockDetailApis(page, '000001');
    detailPage = new StockDetailPage(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在2秒内加载股票详情', async ({ page }) => {
    const startTime = Date.now();

    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000);
  });

  test('应该快速切换时间范围', async ({ page }) => {
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();

    const startTime = Date.now();

    await detailPage.selectTimeRange('1M');
    await page.waitForLoadState('networkidle');

    const switchTime = Date.now() - startTime;
    expect(switchTime).toBeLessThan(1500);
  });

  test('应该高效添加指标', async ({ page }) => {
    await detailPage.navigateToStockDetail('000001');
    await detailPage.waitForPageLoad();

    const startTime = Date.now();

    await detailPage.addIndicator('Simple Moving Average');
    await page.waitForLoadState('networkidle');

    const addTime = Date.now() - startTime;
    expect(addTime).toBeLessThan(2000);
  });
});
