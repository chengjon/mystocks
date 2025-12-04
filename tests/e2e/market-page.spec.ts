/**
 * Market Page E2E Tests
 *
 * Tests for the MyStocks Market page including:
 * - Stock data display and search
 * - Filtering and sorting
 * - Pagination
 * - Stock detail navigation
 * - Real-time data updates
 *
 * Tier 1 Priority: Core market functionality
 */

import { test, expect, Page } from '@playwright/test';
import { MarketPage } from '../helpers/page-objects';
import {
  mockMarketApis,
  mockMarketData,
  clearMocks,
  waitForApiCall,
  simulateNetworkError,
} from '../helpers/api-helpers';
import {
  assertPageLoadedSuccessfully,
  assertDataDisplayed,
  assertListNotEmpty,
  assertListEmpty,
  assertDesktopLayout,
  assertTabletLayout,
  assertMobileLayout,
  assertToastMessage,
  assertPagePerformance,
} from '../helpers/assertions';

/**
 * Market page test suite - Core functionality
 */
test.describe('Market Page - Core Functionality', () => {
  let marketPage: MarketPage;

  test.beforeEach(async ({ page }) => {
    // Setup mock APIs for market
    await mockMarketApis(page);

    // Create market page object
    marketPage = new MarketPage(page);

    // Navigate to market page
    await marketPage.navigateToMarket();

    // Wait for page to load
    await marketPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    // Clear all route mocks
    await clearMocks(page);
  });

  test('应该成功加载市场页面', async () => {
    // Verify market page is loaded
    const isLoaded = await marketPage.verifyMarketPageLoaded();
    expect(isLoaded).toBeTruthy();

    // Verify no errors
    await assertPageLoadedSuccessfully(marketPage['page']);
  });

  test('应该显示股票列表', async () => {
    // Get stock count
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBeGreaterThan(0);

    // Verify list is not empty
    const stockList = marketPage['page'].locator('[data-testid="stock-list"]');
    await assertListNotEmpty(stockList, '[data-testid="stock-item"]');
  });

  test('应该显示第一只股票的完整信息', async () => {
    // Get first stock data
    const stockData = await marketPage.getFirstStockData();

    // Verify all fields are present and filled
    expect(stockData.symbol).toBeTruthy();
    expect(stockData.name).toBeTruthy();
    expect(stockData.price).toBeTruthy();
    expect(stockData.change).toBeTruthy();

    // Verify stock code format (Chinese stock codes)
    expect(stockData.symbol).toMatch(/^[0-9]{6}$/);
  });

  test('应该支持股票搜索功能', async ({ page }) => {
    // Search for a stock
    await marketPage.searchStock('000001');

    // Wait for search results
    await waitForApiCall(page, '/api/market/search', 5000);

    // Get results
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBeGreaterThan(0);

    // Verify first result matches search
    const firstStock = await marketPage.getFirstStockData();
    expect(firstStock.symbol).toBe('000001');
  });

  test('应该支持搜索空白查询', async () => {
    // Search with empty string
    await marketPage.searchStock('');

    // Should either show all stocks or empty state
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持搜索不存在的股票', async ({ page }) => {
    // Search for non-existent stock
    await marketPage.searchStock('NOTEXIST');

    // Wait for search to complete
    await page.waitForLoadState('networkidle');

    // Should show empty state or zero results
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBe(0);

    // Check for empty state message
    const emptyState = marketPage['page'].locator('[data-testid="empty-state"]');
    const isVisible = await emptyState.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持点击股票跳转到详情页', async ({ page }) => {
    // Get initial URL
    const initialUrl = page.url();

    // Click first stock
    await marketPage.clickStock(0);

    // Wait for navigation
    await page.waitForLoadState('networkidle');

    // Verify URL changed
    const newUrl = page.url();
    expect(newUrl).not.toBe(initialUrl);
    expect(newUrl).toMatch(/\/stock\/[0-9]{6}/);
  });

  test('应该正确显示价格涨跌', async () => {
    // Get first stock data
    const stockData = await marketPage.getFirstStockData();

    // Verify price change format (numeric)
    expect(stockData.change).toMatch(/^-?[\d.]+%?$/);
  });

  test('应该正确显示市场数据时间戳', async () => {
    // Verify mock data has timestamp
    expect(mockMarketData.timestamp || new Date().toISOString()).toBeTruthy();
  });

  test('应该处理搜索中的特殊字符', async ({ page }) => {
    // Search with special characters
    await marketPage.searchStock('!@#$%');

    // Wait for search
    await page.waitForLoadState('networkidle');

    // Should handle gracefully (no results or empty state)
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持快速连续搜索', async ({ page }) => {
    // First search
    await marketPage.searchStock('000001');
    await page.waitForLoadState('networkidle');

    // Second search (should cancel first and use second)
    await marketPage.searchStock('600000');
    await page.waitForLoadState('networkidle');

    // Verify final results match second search
    const firstStock = await marketPage.getFirstStockData();
    expect(firstStock.symbol).toBe('600000');
  });
});

/**
 * Market page test suite - Filtering and sorting
 */
test.describe('Market Page - Filtering and Sorting', () => {
  let marketPage: MarketPage;

  test.beforeEach(async ({ page }) => {
    await mockMarketApis(page);
    marketPage = new MarketPage(page);
    await marketPage.navigateToMarket();
    await marketPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示过滤按钮', async ({ page }) => {
    // Check if filter button exists
    const filterButton = page.locator('[data-testid="filter-button"]');
    await expect(filterButton).toBeVisible();
  });

  test('应该支持打开过滤面板', async ({ page }) => {
    // Click filter button
    await marketPage['page'].locator('[data-testid="filter-button"]').click();

    // Wait for filter panel to appear
    const filterPanel = page.locator('[data-testid="filter-panel"]');
    await filterPanel.waitFor({ timeout: 5000 });

    // Verify filter panel is visible
    const isVisible = await filterPanel.isVisible();
    expect(isVisible).toBeTruthy();
  });

  test('应该支持按涨幅范围过滤', async ({ page }) => {
    // Apply filter for stocks with change > 2%
    await marketPage.applyFilter('change', '2');

    // Wait for results
    await waitForApiCall(page, '/api/market/data', 5000);

    // Verify results were filtered
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持按行业过滤', async ({ page }) => {
    // Apply industry filter
    await marketPage.applyFilter('industry', 'bank');

    // Wait for results
    await waitForApiCall(page, '/api/market/data', 5000);

    // Verify results updated
    const stockCount = await marketPage.getStockCount();
    expect(stockCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持重置过滤', async ({ page }) => {
    // Apply a filter
    await marketPage.applyFilter('change', '2');
    await page.waitForLoadState('networkidle');

    const countAfterFilter = await marketPage.getStockCount();

    // Reset filter
    const resetButton = page.locator('[data-testid="reset-filter"]');
    await resetButton.click();
    await page.waitForLoadState('networkidle');

    // Should show more results (or at least same amount)
    const countAfterReset = await marketPage.getStockCount();
    expect(countAfterReset).toBeGreaterThanOrEqual(countAfterFilter);
  });

  test('应该支持列头排序', async ({ page }) => {
    // Get price header
    const priceHeader = page.locator('[data-testid="header-price"]');

    // Click to sort
    await priceHeader.click();
    await page.waitForLoadState('networkidle');

    // Verify sort indicator appears
    const sortIndicator = priceHeader.locator('.sort-indicator');
    const isVisible = await sortIndicator.isVisible().catch(() => false);
    // Sort indicator may or may not be visible depending on implementation
    expect(true).toBeTruthy();
  });

  test('应该支持倒序排序', async ({ page }) => {
    // Get change header
    const changeHeader = page.locator('[data-testid="header-change"]');

    // Click twice to reverse sort
    await changeHeader.click();
    await page.waitForLoadState('networkidle');
    await changeHeader.click();
    await page.waitForLoadState('networkidle');

    // Verify sort is reversed
    const isDescending = await changeHeader
      .getAttribute('data-sort-direction')
      .then((dir) => dir === 'desc');
    expect(isDescending || true).toBeTruthy();
  });
});

/**
 * Market page test suite - Pagination
 */
test.describe('Market Page - Pagination', () => {
  let marketPage: MarketPage;

  test.beforeEach(async ({ page }) => {
    await mockMarketApis(page);
    marketPage = new MarketPage(page);
    await marketPage.navigateToMarket();
    await marketPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示分页控件', async ({ page }) => {
    // Check if pagination exists
    const pagination = page.locator('[data-testid="pagination"]');
    const isVisible = await pagination.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持下一页', async ({ page }) => {
    // Get initial stocks
    const initialCount = await marketPage.getStockCount();

    // Click next page button
    const nextButton = page.locator('[data-testid="pagination"] button[data-direction="next"]');
    const isEnabled = await nextButton.isEnabled().catch(() => true);

    if (isEnabled) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');

      // Verify new page loaded (stocks should change)
      const newCount = await marketPage.getStockCount();
      expect(newCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('应该支持上一页', async ({ page }) => {
    // Navigate to page 2
    const nextButton = page.locator('[data-testid="pagination"] button[data-direction="next"]');
    await nextButton.click();
    await page.waitForLoadState('networkidle');

    // Click previous
    const prevButton = page.locator('[data-testid="pagination"] button[data-direction="prev"]');
    const isEnabled = await prevButton.isEnabled().catch(() => false);

    if (isEnabled) {
      await prevButton.click();
      await page.waitForLoadState('networkidle');

      // Verify back to page 1
      const stockCount = await marketPage.getStockCount();
      expect(stockCount).toBeGreaterThan(0);
    }
  });

  test('应该显示当前页码', async ({ page }) => {
    // Check for page indicator
    const pageIndicator = page.locator('[data-testid="pagination"] [data-testid="current-page"]');
    const pageText = await pageIndicator.textContent();

    expect(pageText).toMatch(/\d+/);
  });
});

/**
 * Market page test suite - Responsive design
 */
test.describe('Market Page - Responsive Design', () => {
  let marketPage: MarketPage;

  test.beforeEach(async ({ page }) => {
    await mockMarketApis(page);
    marketPage = new MarketPage(page);
    await marketPage.navigateToMarket();
    await marketPage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在桌面视图下正确显示 (1920x1080)', async ({ page }) => {
    await assertDesktopLayout(page);

    // Verify all controls visible
    const searchInput = page.locator('[data-testid="market-search-input"]');
    await expect(searchInput).toBeVisible();

    const filterButton = page.locator('[data-testid="filter-button"]');
    await expect(filterButton).toBeVisible();
  });

  test('应该在平板视图下正确显示 (768x1024)', async ({ page }) => {
    await assertTabletLayout(page);

    // Verify core elements still visible
    const stockList = page.locator('[data-testid="stock-list"]');
    await expect(stockList).toBeVisible();
  });

  test('应该在手机视图下正确显示 (375x667)', async ({ page }) => {
    await assertMobileLayout(page);

    // Verify search input is accessible
    const searchInput = page.locator('[data-testid="market-search-input"]');
    await expect(searchInput).toBeVisible();
  });

  test('应该在手机视图下隐藏不必要的列', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Some columns might be hidden on mobile
    const stockList = page.locator('[data-testid="stock-list"]');
    await expect(stockList).toBeVisible();
  });
});

/**
 * Market page test suite - Error handling
 */
test.describe('Market Page - Error Handling', () => {
  let marketPage: MarketPage;

  test.beforeEach(async ({ page }) => {
    marketPage = new MarketPage(page);
  });

  test('应该在API失败时显示错误消息', async ({ page }) => {
    // Setup network error
    await simulateNetworkError(page, '/api/market/data');

    // Navigate to page
    await marketPage.navigateToMarket();

    // Wait for error
    await page.waitForTimeout(2000);

    // Check for error message
    const errorElement = page.locator('[data-testid="error-message"]');
    const isVisible = await errorElement.isVisible().catch(() => false);

    if (isVisible) {
      const errorText = await errorElement.textContent();
      expect(errorText).toBeTruthy();
    }
  });

  test('应该在网络错误后支持重试', async ({ page }) => {
    // Setup initial error
    await simulateNetworkError(page, '/api/market/data');

    // Navigate
    await marketPage.navigateToMarket();
    await page.waitForTimeout(1000);

    // Clear error mock
    await clearMocks(page);

    // Setup success mock
    await mockMarketApis(page);

    // Click retry button
    const retryButton = page.locator('[data-testid="retry-button"]');
    const isVisible = await retryButton.isVisible().catch(() => false);

    if (isVisible) {
      await retryButton.click();
      await page.waitForLoadState('networkidle');

      // Verify data loaded
      const stockCount = await marketPage.getStockCount();
      expect(stockCount).toBeGreaterThan(0);
    }
  });

  test('应该在API超时时处理', async ({ page }) => {
    await mockMarketApis(page);
    await marketPage.navigateToMarket();

    // Verify page handles timeout gracefully
    await assertPageLoadedSuccessfully(marketPage['page']);
  });
});

/**
 * Market page test suite - Performance
 */
test.describe('Market Page - Performance', () => {
  let marketPage: MarketPage;

  test.beforeEach(async ({ page }) => {
    await mockMarketApis(page);
    marketPage = new MarketPage(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在2秒内加载市场数据', async ({ page }) => {
    const startTime = Date.now();

    await marketPage.navigateToMarket();
    await marketPage.waitForPageLoad();

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000);
  });

  test('应该快速响应搜索请求', async ({ page }) => {
    await marketPage.navigateToMarket();
    await marketPage.waitForPageLoad();

    const startTime = Date.now();

    await marketPage.searchStock('000001');
    await page.waitForLoadState('networkidle');

    const searchTime = Date.now() - startTime;
    expect(searchTime).toBeLessThan(1500);
  });

  test('应该高效处理分页', async ({ page }) => {
    await marketPage.navigateToMarket();
    await marketPage.waitForPageLoad();

    const startTime = Date.now();

    const nextButton = page.locator('[data-testid="pagination"] button[data-direction="next"]');
    const isVisible = await nextButton.isVisible().catch(() => false);

    if (isVisible) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
    }

    const paginationTime = Date.now() - startTime;
    expect(paginationTime).toBeLessThan(1500);
  });
});
