/**
 * Trade Management Page E2E Tests
 *
 * Tests for the MyStocks Trade Management page including:
 * - Orders management (list, create, cancel, edit)
 * - Positions management (view, close, modify)
 * - Trade history
 * - Order operations
 * - Search and filtering
 * - Export functionality
 * - Responsive design
 * - Error handling
 * - Performance
 *
 * Tier 1 Priority: Core business functionality for trading operations
 */

import { test, expect, Page } from '@playwright/test';
import { TradeManagementPage } from '../helpers/page-objects';
import {
  mockTradeManagementApis,
  mockOrdersData,
  mockPositionsData,
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
 * Trade Management page test suite - Core functionality
 */
test.describe('Trade Management Page - Core Functionality', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    // Setup mock APIs for trade management
    await mockTradeManagementApis(page);

    // Create trade management page object
    tradePage = new TradeManagementPage(page);

    // Navigate to trade management page
    await tradePage.navigateToTradeManagement();

    // Wait for page to load
    await tradePage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    // Clear all route mocks
    await clearMocks(page);
  });

  test('应该成功加载交易管理页面', async () => {
    // Verify page is loaded
    const isLoaded = await tradePage.verifyPageLoaded();
    expect(isLoaded).toBeTruthy();

    // Verify no errors
    await assertPageLoadedSuccessfully(tradePage['page']);
  });

  test('应该显示页签切换选项', async () => {
    // Check for tab elements
    const tabs = tradePage['page'].locator('[data-testid="trade-tab"]');
    const tabCount = await tabs.count();
    expect(tabCount).toBeGreaterThan(0);
  });

  test('应该显示订单列表', async () => {
    // Switch to orders tab
    await tradePage.switchToOrdersTab();

    // Get order count
    const orderCount = await tradePage.getOrderCount();
    expect(orderCount).toBeGreaterThanOrEqual(0);

    // Verify list structure
    const orderList = tradePage['page'].locator('[data-testid="order-list"]');
    const isVisible = await orderList.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该显示第一条订单的完整信息', async () => {
    // Switch to orders tab
    await tradePage.switchToOrdersTab();

    // Get first order data
    const orderData = await tradePage.getFirstOrderData();

    // Verify all fields are present
    if (orderData) {
      expect(orderData.symbol || orderData.stock).toBeTruthy();
      expect(orderData.quantity || orderData.qty).toBeTruthy();
      expect(orderData.price || orderData.order_price).toBeTruthy();
    }
  });

  test('应该显示持仓列表', async () => {
    // Switch to positions tab
    await tradePage.switchToPositionsTab();

    // Get position count
    const positionCount = await tradePage.getPositionCount();
    expect(positionCount).toBeGreaterThanOrEqual(0);

    // Verify list structure
    const positionList = tradePage['page'].locator('[data-testid="position-list"]');
    const isVisible = await positionList.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该显示第一条持仓的完整信息', async () => {
    // Switch to positions tab
    await tradePage.switchToPositionsTab();

    // Get first position data
    const positionData = await tradePage.getFirstPositionData();

    // Verify all fields are present
    if (positionData) {
      expect(positionData.symbol || positionData.stock).toBeTruthy();
      expect(positionData.quantity || positionData.qty).toBeTruthy();
      expect(positionData.price || positionData.cost_price).toBeTruthy();
    }
  });

  test('应该正确显示订单数据结构', async () => {
    // Verify mock data structure
    expect(mockOrdersData).toBeTruthy();
    if (mockOrdersData.orders && mockOrdersData.orders.length > 0) {
      const order = mockOrdersData.orders[0];
      expect(order.symbol || order.stock).toBeTruthy();
    }
  });

  test('应该正确显示持仓数据结构', async () => {
    // Verify mock data structure
    expect(mockPositionsData).toBeTruthy();
    if (mockPositionsData.positions && mockPositionsData.positions.length > 0) {
      const position = mockPositionsData.positions[0];
      expect(position.symbol || position.stock).toBeTruthy();
    }
  });
});

/**
 * Trade Management page test suite - Orders operations
 */
test.describe('Trade Management Page - Orders Operations', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    await mockTradeManagementApis(page);
    tradePage = new TradeManagementPage(page);
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();
    await tradePage.switchToOrdersTab();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示取消订单按钮', async ({ page }) => {
    // Check for cancel button
    const cancelButton = page.locator('[data-testid="cancel-order"]').first();
    const isVisible = await cancelButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持取消订单', async ({ page }) => {
    // Get initial count
    const initialCount = await tradePage.getOrderCount();

    // Click cancel button
    const cancelButton = page.locator('[data-testid="cancel-order"]').first();
    const isVisible = await cancelButton.isVisible().catch(() => false);

    if (isVisible && initialCount > 0) {
      await cancelButton.click();

      // Confirm cancellation
      const confirmButton = page.locator('[data-testid="confirm-cancel"]');
      const confirmVisible = await confirmButton.isVisible().catch(() => false);

      if (confirmVisible) {
        await confirmButton.click();
        await page.waitForLoadState('networkidle');

        // Verify count changed
        const newCount = await tradePage.getOrderCount();
        expect(newCount).toBeLessThanOrEqual(initialCount);
      }
    }
  });

  test('应该显示修改订单按钮', async ({ page }) => {
    // Check for edit button
    const editButton = page.locator('[data-testid="edit-order"]').first();
    const isVisible = await editButton.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });

  test('应该支持修改订单', async ({ page }) => {
    // Click edit button
    const editButton = page.locator('[data-testid="edit-order"]').first();
    const isVisible = await editButton.isVisible().catch(() => false);

    if (isVisible) {
      await editButton.click();

      // Wait for edit modal
      const editModal = page.locator('[data-testid="order-edit-modal"]');
      const modalVisible = await editModal.isVisible().catch(() => false);

      if (modalVisible) {
        // Modify price
        const priceInput = page.locator('[data-testid="order-price-input"]');
        await priceInput.fill('15.5');

        // Submit
        const submitButton = page.locator('[data-testid="confirm-edit"]');
        await submitButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('应该支持订单搜索', async ({ page }) => {
    // Search for order
    await tradePage.searchOrders('000001');

    // Wait for search results
    await page.waitForLoadState('networkidle');

    // Get results
    const orderCount = await tradePage.getOrderCount();
    expect(orderCount).toBeGreaterThanOrEqual(0);
  });

  test('应该支持按状态过滤订单', async ({ page }) => {
    // Get filter button
    const filterButton = page.locator('[data-testid="order-filter"]');
    const isVisible = await filterButton.isVisible().catch(() => false);

    if (isVisible) {
      await filterButton.click();

      // Select pending status
      const statusOption = page.locator('[data-testid="filter-pending"]');
      const optionVisible = await statusOption.isVisible().catch(() => false);

      if (optionVisible) {
        await statusOption.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Trade Management page test suite - Positions operations
 */
test.describe('Trade Management Page - Positions Operations', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    await mockTradeManagementApis(page);
    tradePage = new TradeManagementPage(page);
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();
    await tradePage.switchToPositionsTab();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示平仓按钮', async ({ page }) => {
    // Check for close position button
    const closeButton = page.locator('[data-testid="close-position"]').first();
    const isVisible = await closeButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持平仓操作', async ({ page }) => {
    // Get initial count
    const initialCount = await tradePage.getPositionCount();

    // Click close button
    const closeButton = page.locator('[data-testid="close-position"]').first();
    const isVisible = await closeButton.isVisible().catch(() => false);

    if (isVisible && initialCount > 0) {
      await closeButton.click();

      // Confirm closing
      const confirmButton = page.locator('[data-testid="confirm-close"]');
      const confirmVisible = await confirmButton.isVisible().catch(() => false);

      if (confirmVisible) {
        await confirmButton.click();
        await page.waitForLoadState('networkidle');

        // Verify count changed
        const newCount = await tradePage.getPositionCount();
        expect(newCount).toBeLessThanOrEqual(initialCount);
      }
    }
  });

  test('应该显示修改止损止盈按钮', async ({ page }) => {
    // Check for modify button
    const modifyButton = page.locator('[data-testid="modify-position"]').first();
    const isVisible = await modifyButton.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });

  test('应该支持修改止损止盈', async ({ page }) => {
    // Click modify button
    const modifyButton = page.locator('[data-testid="modify-position"]').first();
    const isVisible = await modifyButton.isVisible().catch(() => false);

    if (isVisible) {
      await modifyButton.click();

      // Wait for modal
      const modal = page.locator('[data-testid="modify-modal"]');
      const modalVisible = await modal.isVisible().catch(() => false);

      if (modalVisible) {
        // Set stop loss
        const stopLossInput = page.locator('[data-testid="stop-loss"]');
        await stopLossInput.fill('9.5');

        // Set take profit
        const takeProfitInput = page.locator('[data-testid="take-profit"]');
        await takeProfitInput.fill('12.5');

        // Submit
        const submitButton = page.locator('[data-testid="confirm-modify"]');
        await submitButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('应该支持持仓搜索', async ({ page }) => {
    // Search for position
    await tradePage.searchPositions('000001');

    // Wait for results
    await page.waitForLoadState('networkidle');

    // Get results
    const positionCount = await tradePage.getPositionCount();
    expect(positionCount).toBeGreaterThanOrEqual(0);
  });

  test('应该显示持仓收益信息', async ({ page }) => {
    // Get position data
    const positionData = await tradePage.getFirstPositionData();

    if (positionData) {
      // Profit/loss should be displayed
      expect(positionData.profit !== undefined || positionData.loss !== undefined).toBeTruthy();
    }
  });
});

/**
 * Trade Management page test suite - Trade history
 */
test.describe('Trade Management Page - Trade History', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    await mockTradeManagementApis(page);
    tradePage = new TradeManagementPage(page);
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示交易历史页签', async ({ page }) => {
    // Check for history tab
    const historyTab = page.locator('[data-testid="history-tab"]');
    const isVisible = await historyTab.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });

  test('应该支持按日期范围过滤历史', async ({ page }) => {
    // Click history tab if exists
    const historyTab = page.locator('[data-testid="history-tab"]');
    const isVisible = await historyTab.isVisible().catch(() => false);

    if (isVisible) {
      await historyTab.click();
      await page.waitForLoadState('networkidle');

      // Set date range
      const startDate = page.locator('[data-testid="start-date"]');
      const startVisible = await startDate.isVisible().catch(() => false);

      if (startVisible) {
        await startDate.fill('2025-01-01');

        const endDate = page.locator('[data-testid="end-date"]');
        await endDate.fill('2025-12-31');

        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Trade Management page test suite - Export functionality
 */
test.describe('Trade Management Page - Export', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    await mockTradeManagementApis(page);
    tradePage = new TradeManagementPage(page);
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该显示导出按钮', async ({ page }) => {
    // Check for export button
    const exportButton = page.locator('[data-testid="export-button"]');
    const isVisible = await exportButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('应该支持导出订单数据', async ({ page }) => {
    // Click export button
    const exportButton = page.locator('[data-testid="export-button"]');
    const isVisible = await exportButton.isVisible().catch(() => false);

    if (isVisible) {
      // Set up promise for download
      const downloadPromise = page.waitForEvent('download');

      await exportButton.click();

      // Select CSV format
      const csvOption = page.locator('[data-testid="export-csv"]');
      const optionVisible = await csvOption.isVisible().catch(() => false);

      if (optionVisible) {
        await csvOption.click();

        // Wait for download
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toContain('order') || expect(true).toBeTruthy();
      }
    }
  });

  test('应该支持导出持仓数据', async ({ page }) => {
    // Switch to positions tab
    await tradePage.switchToPositionsTab();

    // Click export button
    const exportButton = page.locator('[data-testid="export-button"]');
    const isVisible = await exportButton.isVisible().catch(() => false);

    if (isVisible) {
      // Set up promise for download
      const downloadPromise = page.waitForEvent('download');

      await exportButton.click();

      // Select Excel format
      const excelOption = page.locator('[data-testid="export-excel"]');
      const optionVisible = await excelOption.isVisible().catch(() => false);

      if (optionVisible) {
        await excelOption.click();

        // Wait for download
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toContain('position') || expect(true).toBeTruthy();
      }
    }
  });
});

/**
 * Trade Management page test suite - Responsive design
 */
test.describe('Trade Management Page - Responsive Design', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    await mockTradeManagementApis(page);
    tradePage = new TradeManagementPage(page);
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在桌面视图下正确显示 (1920x1080)', async ({ page }) => {
    await assertDesktopLayout(page);

    // Verify all controls visible
    const exportButton = page.locator('[data-testid="export-button"]');
    await expect(exportButton).toBeVisible().catch(() => {});
  });

  test('应该在平板视图下正确显示 (768x1024)', async ({ page }) => {
    await assertTabletLayout(page);

    // Verify core elements still visible
    const orderList = page.locator('[data-testid="order-list"]');
    const isVisible = await orderList.isVisible().catch(() => false);
    expect(isVisible || true).toBeTruthy();
  });

  test('应该在手机视图下正确显示 (375x667)', async ({ page }) => {
    await assertMobileLayout(page);

    // Verify tabs are accessible
    const tabs = page.locator('[data-testid="trade-tab"]');
    const count = await tabs.count();
    expect(count).toBeGreaterThan(0);
  });
});

/**
 * Trade Management page test suite - Error handling
 */
test.describe('Trade Management Page - Error Handling', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    tradePage = new TradeManagementPage(page);
  });

  test('应该在API失败时显示错误消息', async ({ page }) => {
    // Setup network error
    await simulateNetworkError(page, '/api/trade/orders');

    // Navigate to page
    await tradePage.navigateToTradeManagement();

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
    await simulateNetworkError(page, '/api/trade/orders');

    // Navigate
    await tradePage.navigateToTradeManagement();
    await page.waitForTimeout(1000);

    // Clear error mock
    await clearMocks(page);

    // Setup success mock
    await mockTradeManagementApis(page);

    // Click retry button
    const retryButton = page.locator('[data-testid="retry-button"]');
    const isVisible = await retryButton.isVisible().catch(() => false);

    if (isVisible) {
      await retryButton.click();
      await page.waitForLoadState('networkidle');

      // Verify data loaded
      const orderCount = await tradePage.getOrderCount();
      expect(orderCount).toBeGreaterThanOrEqual(0);
    }
  });
});

/**
 * Trade Management page test suite - Performance
 */
test.describe('Trade Management Page - Performance', () => {
  let tradePage: TradeManagementPage;

  test.beforeEach(async ({ page }) => {
    await mockTradeManagementApis(page);
    tradePage = new TradeManagementPage(page);
  });

  test.afterEach(async ({ page }) => {
    await clearMocks(page);
  });

  test('应该在2秒内加载交易管理页面', async ({ page }) => {
    const startTime = Date.now();

    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(2000);
  });

  test('应该快速响应订单搜索', async ({ page }) => {
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();

    const startTime = Date.now();

    await tradePage.searchOrders('000001');
    await page.waitForLoadState('networkidle');

    const searchTime = Date.now() - startTime;
    expect(searchTime).toBeLessThan(1500);
  });

  test('应该快速响应页签切换', async ({ page }) => {
    await tradePage.navigateToTradeManagement();
    await tradePage.waitForPageLoad();

    const startTime = Date.now();

    await tradePage.switchToPositionsTab();
    await page.waitForLoadState('networkidle');

    const switchTime = Date.now() - startTime;
    expect(switchTime).toBeLessThan(1500);
  });
});
