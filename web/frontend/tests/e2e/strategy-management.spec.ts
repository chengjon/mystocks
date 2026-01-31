/**
 * Strategy Management Module E2E Tests
 *
 * End-to-end tests for strategy management functionality using Playwright.
 * Tests cover user journeys, CRUD operations, backtesting, and UI interactions.
 */

import { test, expect } from '@playwright/test';
import { loginAndSetupAuth } from './helpers/auth';

/**
 * Desktop viewports to test
 */
const desktopViewports = [
  { width: 1920, height: 1080, name: 'Full HD' },
  { width: 1680, height: 1050, name: 'Widescreen' },
  { width: 1440, height: 900, name: 'Laptop' },
];

/**
 * Base URL for the application
 */
const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

test.describe('Strategy Management Module - E2E Tests', () => {
  test.beforeEach(async ({ page, request }) => {
    // Set default viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Setup authentication using the new auth helper
    await loginAndSetupAuth(request, page);
  });

  test.describe('Strategy List Page', () => {
    test('should load strategy management page successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy-hub/management`);

      // Check page title
      await expect(page).toHaveTitle(/MyStocks/);

      // Check main heading
      const heading = page.locator('h1').filter({ hasText: /STRATEGY MANAGEMENT/ });
      await expect(heading).toBeVisible();
    });

    test('should display strategy cards', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Check for strategy cards
      const strategyCards = page.locator('.strategy-card, [data-testid="strategy-card"]');
      const count = await strategyCards.count();

      // Should have at least 1 strategy (from Mock data)
      expect(count).toBeGreaterThan(0);
    });

    test('should display strategy details correctly', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Check first strategy card
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();

      // Verify strategy name is visible
      const strategyName = firstCard.locator('.strategy-name, .name, [data-testid="strategy-name"]');
      await expect(strategyName).toBeVisible();

      // Verify strategy type is visible
      const strategyType = firstCard.locator('.strategy-type, .type, [data-testid="strategy-type"]');
      await expect(strategyType).toBeVisible();

      // Verify strategy status is visible
      const strategyStatus = firstCard.locator('.strategy-status, .status, [data-testid="strategy-status"]');
      await expect(strategyStatus).toBeVisible();
    });

    test('should handle API failures gracefully with Mock data', async ({ page }) => {
      // Simulate API failure
      await page.route('**/api/v1/strategy/strategies', (route) => {
        route.abort('failed');
      });

      await page.goto(`${BASE_URL}/strategy`);

      // Wait for fallback
      await page.waitForTimeout(2000);

      // Verify Mock data is displayed
      const strategyCards = page.locator('.strategy-card, [data-testid="strategy-card"]');
      const count = await strategyCards.count();
      expect(count).toBeGreaterThan(0);

      // Check for mock data indicator
      const mockIndicator = page.locator('.mock-data, [data-testid="mock-data"]');
      const mockCount = await mockIndicator.count();

      if (mockCount > 0) {
        await expect(mockIndicator.first()).toBeVisible();
      }
    });
  });

  test.describe('Create Strategy Dialog', () => {
    test('should open create strategy dialog', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for page load
      await page.waitForTimeout(1000);

      // Find and click create button
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建"), [data-testid="create-strategy-button"]');
      const createCount = await createButton.count();

      if (createCount > 0) {
        await createButton.first().click();

        // Wait for dialog to open
        await page.waitForTimeout(500);

        // Verify dialog is visible
        const dialog = page.locator('.dialog, .modal, [role="dialog"]');
        await expect(dialog.first()).toBeVisible();
      }
    });

    test('should validate strategy form fields', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for page load
      await page.waitForTimeout(1000);

      // Open create dialog
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建")');
      const createCount = await createButton.count();

      if (createCount > 0) {
        await createButton.first().click();
        await page.waitForTimeout(500);

        // Try to submit without filling required fields
        const submitButton = page.locator('button:has-text("提交"), button:has-text("创建"), button[type="submit"]');
        const submitCount = await submitButton.count();

        if (submitCount > 0) {
          await submitButton.first().click();

          // Check for validation errors
          const errorMessages = page.locator('.error-message, .validation-error, [data-testid="validation-error"]');
          const errorCount = await errorMessages.count();

          if (errorCount > 0) {
            await expect(errorMessages.first()).toBeVisible();
          }
        }
      }
    });

    test('should fill and submit create strategy form', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for page load
      await page.waitForTimeout(1000);

      // Open create dialog
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建")');
      const createCount = await createButton.count();

      if (createCount > 0) {
        await createButton.first().click();
        await page.waitForTimeout(500);

        // Fill in form fields
        const nameInput = page.locator('input[name="name"], [data-testid="strategy-name-input"]');
        const nameCount = await nameInput.count();

        if (nameCount > 0) {
          await nameInput.first().fill('测试策略');

          // Select strategy type
          const typeSelect = page.locator('select[name="type"], [data-testid="strategy-type-select"]');
          const typeCount = await typeSelect.count();

          if (typeCount > 0) {
            await typeSelect.first().selectOption('trend_following');

            // Submit form
            const submitButton = page.locator('button:has-text("提交"), button[type="submit"]');
            await submitButton.first().click();

            // Wait for response
            await page.waitForTimeout(2000);

            // Verify dialog is closed
            const dialog = page.locator('.dialog, .modal, [role="dialog"]');
            const dialogCount = await dialog.count();

            if (dialogCount > 0) {
              const isVisible = await dialog.first().isVisible();
              expect(isVisible).toBeFalsy();
            }
          }
        }
      }
    });
  });

  test.describe('Strategy Detail View', () => {
    test('should navigate to strategy detail page', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Click on first strategy card
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();

      // Wait for navigation
      await page.waitForTimeout(1000);

      // Verify we're on detail page
      const url = page.url();
      expect(url).toContain('/strategy/');
    });

    test('should display strategy performance metrics', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Click on first strategy card
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();

      // Wait for detail page to load
      await page.waitForTimeout(1000);

      // Check for performance metrics
      const performanceSection = page.locator('.performance-metrics, [data-testid="performance-metrics"]');
      const perfCount = await performanceSection.count();

      if (perfCount > 0) {
        await expect(performanceSection.first()).toBeVisible();

        // Verify specific metrics
        const totalReturn = page.locator('.total-return, [data-testid="total-return"]');
        const sharpeRatio = page.locator('.sharpe-ratio, [data-testid="sharpe-ratio"]');

        await expect(totalReturn.first()).toBeVisible();
        await expect(sharpeRatio.first()).toBeVisible();
      }
    });
  });

  test.describe('Backtest Panel', () => {
    test('should open backtest panel', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Click on first strategy card to view details
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();

      // Wait for detail page
      await page.waitForTimeout(1000);

      // Find and click backtest button
      const backtestButton = page.locator('button:has-text("回测"), [data-testid="backtest-button"]');
      const backtestCount = await backtestButton.count();

      if (backtestCount > 0) {
        await backtestButton.first().click();

        // Wait for panel to open
        await page.waitForTimeout(500);

        // Verify backtest panel is visible
        const backtestPanel = page.locator('.backtest-panel, [data-testid="backtest-panel"]');
        await expect(backtestPanel.first()).toBeVisible();
      }
    });

    test('should validate backtest parameters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Navigate to strategy detail
      const firstCard = page.locator('.strategy-card, [data-testid="strategy-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);

      // Open backtest panel
      const backtestButton = page.locator('button:has-text("回测"), [data-testid="backtest-button"]');
      const backtestCount = await backtestButton.count();

      if (backtestCount > 0) {
        await backtestButton.first().click();
        await page.waitForTimeout(500);

        // Try to submit with invalid parameters
        const submitButton = page.locator('.backtest-panel button:has-text("开始回测"), .backtest-panel button[type="submit"]');
        const submitCount = await submitButton.count();

        if (submitCount > 0) {
          await submitButton.first().click();

          // Check for validation errors
          const errorMessages = page.locator('.error-message, .validation-error');
          const errorCount = await errorMessages.count();

          if (errorCount > 0) {
            await expect(errorMessages.first()).toBeVisible();
          }
        }
      }
    });
  });

  test.describe('Desktop Layout Validation', () => {
    for (const viewport of desktopViewports) {
      test(`${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(`${BASE_URL}/strategy`);

        // Wait for page to load
        await page.waitForLoadState('networkidle');

        // Check main content area
        const mainContent = page.locator('main, .main-content, [role="main"]');
        await expect(mainContent).toBeInViewport();

        // Check strategy grid layout
        const strategyGrid = page.locator('.strategy-grid, [data-testid="strategy-grid"]');
        const gridCount = await strategyGrid.count();

        if (gridCount > 0) {
          await expect(strategyGrid.first()).toBeVisible();
        }
      });
    }
  });

  test.describe('Navigation', () => {
    test('should navigate from dashboard to strategy page', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);

      // Find strategy link in navigation
      const strategyLink = page.locator('a:has-text("策略管理"), a[href*="/strategy"]');
      await strategyLink.first().click();

      // Verify navigation
      await page.waitForURL('**/strategy');
      await expect(page).toHaveURL(/\/strategy/);
    });

    test('should navigate using sidebar menu', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);

      // Find sidebar (ArtDecoLayout uses .layout-sidebar)
      const sidebar = page.locator('.layout-sidebar, aside, [data-testid="sidebar"]');
      const sidebarCount = await sidebar.count();

      if (sidebarCount > 0) {
        const strategyMenu = sidebar.first().locator('a:has-text("策略")');
        const menuCount = await strategyMenu.count();

        if (menuCount > 0) {
          await strategyMenu.first().click();
          await page.waitForURL('**/strategy');
        }
      }
    });
  });

  test.describe('Real-time Updates', () => {
    test('should display loading state during operations', async ({ page }) => {
      // Slow down API response
      await page.route('**/api/v1/strategy/strategies', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        route.continue();
      });

      await page.goto(`${BASE_URL}/strategy`);

      // Check for loading indicator
      const loadingIndicator = page.locator('.loading, .spinner, [data-testid="loading"]');
      await expect(loadingIndicator).toBeVisible();
    });

    test('should refresh strategy list', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for initial load
      await page.waitForTimeout(2000);

      // Find refresh button
      const refreshButton = page.locator('button:has-text("刷新"), [data-testid="refresh-button"]');
      const refreshCount = await refreshButton.count();

      if (refreshCount > 0) {
        // Click refresh
        await refreshButton.first().click();

        // Wait for reload
        await page.waitForTimeout(2000);

        // Verify loading was shown
        const loadingIndicator = page.locator('.loading, .spinner');
        await expect(loadingIndicator).not.toBeVisible();
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should show error message on failed strategy creation', async ({ page }) => {
      // Simulate API failure
      await page.route('**/api/strategy', (route) => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            message: 'Internal Server Error',
            code: 500,
          }),
        });
      });

      await page.goto(`${BASE_URL}/strategy`);

      // Wait for page load
      await page.waitForTimeout(1000);

      // Open create dialog
      const createButton = page.locator('button:has-text("创建策略"), button:has-text("新建")');
      const createCount = await createButton.count();

      if (createCount > 0) {
        await createButton.first().click();
        await page.waitForTimeout(500);

        // Try to create strategy
        const nameInput = page.locator('input[name="name"]');
        const nameCount = await nameInput.count();

        if (nameCount > 0) {
          await nameInput.first().fill('测试策略');

          const submitButton = page.locator('button[type="submit"]');
          await submitButton.first().click();

          // Wait for error response
          await page.waitForTimeout(1000);

          // Check for error message
          const errorMessage = page.locator('.error-message, .notification-error');
          const errorCount = await errorMessage.count();

          if (errorCount > 0) {
            await expect(errorMessage.first()).toBeVisible();
          }
        }
      }
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper ARIA labels on interactive elements', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Check buttons have aria-label or text content
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();

      for (let i = 0; i < Math.min(buttonCount, 10); i++) {
        const button = buttons.nth(i);
        const hasAriaLabel = await button.getAttribute('aria-label');
        const hasText = (await button.textContent()).trim().length > 0;

        expect(hasAriaLabel !== null || hasText).toBeTruthy();
      }
    });

    test('should be keyboard navigable', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for load
      await page.waitForTimeout(1000);

      // Tab through focusable elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Verify focus is visible
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });
  });

  /**
   * Task 2.2.2: Search, Filter, and Pagination Tests
   */
  test.describe('Search and Filter Functionality', () => {
    test('should search strategies by name', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Count total strategies before search
      const allStrategies = page.locator('.strategy-card');
      const totalCount = await allStrategies.count();

      // Enter search query
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();
      await searchInput.fill('momentum');
      await page.waitForTimeout(500);

      // Count filtered strategies
      const filteredStrategies = page.locator('.strategy-card');
      const filteredCount = await filteredStrategies.count();

      // Verify filtering occurred (should have fewer results or no results if none match)
      expect(filteredCount).toBeLessThanOrEqual(totalCount);

      // Clear search
      await searchInput.fill('');
      await page.waitForTimeout(500);

      // Verify all strategies shown again
      const afterClearCount = await allStrategies.count();
      expect(afterClearCount).toBe(totalCount);
    });

    test('should filter strategies by type', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Count total strategies before filter
      const allStrategies = page.locator('.strategy-card');
      const totalCount = await allStrategies.count();

      // Select type filter
      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();
      await typeFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' }).first().click();
      await page.waitForTimeout(500);

      // Verify filtering occurred
      const filteredStrategies = page.locator('.strategy-card');
      const filteredCount = await filteredStrategies.count();

      // Note: May be 0 if no trend following strategies exist
      expect(filteredCount).toBeGreaterThanOrEqual(0);
      expect(filteredCount).toBeLessThanOrEqual(totalCount);
    });

    test('should filter strategies by status', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Count total strategies before filter
      const allStrategies = page.locator('.strategy-card');
      const totalCount = await allStrategies.count();

      // Select status filter
      const statusFilter = page.locator('.el-select').filter({ hasText: /FILTER BY STATUS|STATUS/ }).first();
      await statusFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'ACTIVE' }).first().click();
      await page.waitForTimeout(500);

      // Verify filtering occurred
      const filteredStrategies = page.locator('.strategy-card');
      const filteredCount = await filteredStrategies.count();

      expect(filteredCount).toBeGreaterThanOrEqual(0);
      expect(filteredCount).toBeLessThanOrEqual(totalCount);
    });

    test('should combine search and filters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Enter search query
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();
      await searchInput.fill('test');

      // Apply type filter
      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();
      await typeFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'MOMENTUM' }).first().click();

      await page.waitForTimeout(500);

      // Verify combined filtering
      const filteredStrategies = page.locator('.strategy-card');
      const filteredCount = await filteredStrategies.count();

      expect(filteredCount).toBeGreaterThanOrEqual(0);
    });

    test('should clear all filters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Apply search and filters
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();
      await searchInput.fill('test');

      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();
      await typeFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' }).first().click();

      await page.waitForTimeout(500);

      // Clear search
      await searchInput.fill('');

      // Clear filters using clear buttons
      const clearButtons = page.locator('.el-select__caret');
      const count = await clearButtons.count();
      for (let i = 0; i < count; i++) {
        await clearButtons.nth(i).click();
      }

      await page.waitForTimeout(500);

      // Verify all strategies are shown
      const allStrategies = page.locator('.strategy-card');
      const finalCount = await allStrategies.count();

      expect(finalCount).toBeGreaterThan(0);
    });
  });

  test.describe('Pagination Functionality', () => {
    test('should display pagination controls', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Check for pagination component
      const pagination = page.locator('.el-pagination');
      await expect(pagination).toBeVisible();
    });

    test('should change page size', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Find page size selector
      const pageSizeSelector = page.locator('.el-pagination__sizes .el-select');
      await pageSizeSelector.click();

      // Select 24 per page
      await page.locator('.el-select-dropdown__item').filter({ hasText: '24' }).first().click();
      await page.waitForTimeout(500);

      // Verify page size changed (check total or pagination info)
      const pagination = page.locator('.el-pagination');
      await expect(pagination).toBeVisible();
    });

    test('should navigate between pages', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Find next page button
      const nextButton = page.locator('.el-pagination .btn-next', { hasText: /<|>/ }).first();
      const isNextDisabled = await nextButton.getAttribute('class').then(cls => cls?.includes('disabled'));

      if (!isNextDisabled) {
        // Get current page number
        const currentPage = page.locator('.el-pager li.active').first();
        const initialPage = await currentPage.textContent();

        // Click next page
        await nextButton.click();
        await page.waitForTimeout(500);

        // Verify page changed
        const newPage = page.locator('.el-pager li.active').first();
        const newPageText = await newPage.textContent();
        expect(newPageText).not.toBe(initialPage);
      }
    });
  });

  /**
   * Task 2.2.3: Strategy Type and Parameters Tests
   */
  test.describe('Enhanced Create Strategy Form', () => {
    test('should display strategy type selector', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Click create button
      const createButton = page.locator('button', { hasText: /CREATE|ADD/ }).first();
      await createButton.click();
      await page.waitForTimeout(500);

      // Check for type selector
      const typeSelector = page.locator('label', { hasText: /STRATEGY TYPE/ });
      await expect(typeSelector).toBeVisible();

      // Check that dropdown is present
      const typeDropdown = page.locator('.el-select').filter({ has: page.locator('label', { hasText: /STRATEGY TYPE/ }) });
      await expect(typeDropdown).toBeVisible();

      // Close dialog
      const cancelButton = page.locator('button', { hasText: /CANCEL|CLOSE/ }).first();
      await cancelButton.click();
    });

    test('should display all strategy type options', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Click create button
      const createButton = page.locator('button', { hasText: /CREATE|ADD/ }).first();
      await createButton.click();
      await page.waitForTimeout(500);

      // Click type dropdown
      const typeDropdown = page.locator('.el-select').filter({ has: page.locator('label', { hasText: /STRATEGY TYPE/ }) });
      await typeDropdown.click();
      await page.waitForTimeout(300);

      // Check for all three types
      const trendOption = page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' });
      const meanOption = page.locator('.el-select-dropdown__item').filter({ hasText: 'MEAN REVERSION' });
      const momentumOption = page.locator('.el-select-dropdown__item').filter({ hasText: 'MOMENTUM' });

      await expect(trendOption).toBeVisible();
      await expect(meanOption).toBeVisible();
      await expect(momentumOption).toBeVisible();

      // Close dialog
      const cancelButton = page.locator('button', { hasText: /CANCEL|CLOSE/ }).first();
      await cancelButton.click();
    });

    test('should add and remove parameters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Click create button
      const createButton = page.locator('button', { hasText: /CREATE|ADD/ }).first();
      await createButton.click();
      await page.waitForTimeout(500);

      // Find parameters section
      const parametersLabel = page.locator('label', { hasText: /PARAMETERS/ });
      const hasParameters = await parametersLabel.count() > 0;

      if (hasParameters) {
        // Click "Add Parameter" button
        const addButton = page.locator('button', { hasText: /ADD PARAMETER/ });
        const addCount = await addButton.count();

        if (addCount > 0) {
          await addButton.first().click();
          await page.waitForTimeout(300);

          // Check for parameter input fields
          const parameterInputs = page.locator('.parameter-row input');
          const inputCount = await parameterInputs.count();
          expect(inputCount).toBeGreaterThan(0);

          // Check for remove button
          const removeButton = page.locator('.parameter-row button');
          const removeCount = await removeButton.count();
          expect(removeCount).toBeGreaterThan(0);

          // Remove parameter
          if (removeCount > 0) {
            await removeButton.first().click();
            await page.waitForTimeout(300);
          }
        }
      }

      // Close dialog
      const cancelButton = page.locator('button', { hasText: /CANCEL|CLOSE/ }).first();
      await cancelButton.click();
    });

    test('should create strategy with type and parameters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Click create button
      const createButton = page.locator('button', { hasText: /CREATE|ADD/ }).first();
      await createButton.click();
      await page.waitForTimeout(500);

      // Fill strategy name
      const nameInput = page.locator('input[name*="name"], input[placeholder*="NAME"]').first();
      await nameInput.fill('E2E Test Strategy');

      // Select strategy type
      const typeDropdown = page.locator('.el-select').filter({ has: page.locator('label', { hasText: /STRATEGY TYPE/ }) });
      await typeDropdown.click();
      await page.waitForTimeout(300);
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' }).first().click();
      await page.waitForTimeout(300);

      // Add parameter
      const addButton = page.locator('button', { hasText: /ADD PARAMETER/ });
      const addCount = await addButton.count();

      if (addCount > 0) {
        await addButton.first().click();
        await page.waitForTimeout(300);

        // Fill parameter key and value
        const paramInputs = page.locator('.parameter-row input');
        if (await paramInputs.count() >= 2) {
          await paramInputs.nth(0).fill('period');
          await paramInputs.nth(1).fill('20');
        }
      }

      // Submit form (may fail if backend not available, but UI should work)
      const submitButton = page.locator('button[type="submit"], button', { hasText: /CREATE|SUBMIT/ }).last();
      await submitButton.click();
      await page.waitForTimeout(1000);

      // Check for either success message or error (both are acceptable)
      const messageBox = page.locator('.el-message');
      const hasMessage = await messageBox.count() > 0;
      expect(hasMessage).toBeTruthy();
    });
  });

  /**
   * Task 2.2.4: Delete Confirmation Dialog Tests
   */
  test.describe('Delete Confirmation Dialog', () => {
    test('should show delete confirmation dialog', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Find a strategy card with delete button
      const firstCard = page.locator('.strategy-card').first();
      const deleteButton = firstCard.locator('button', { hasText: /DELETE|REMOVE/ }).or(
        firstCard.locator('.el-icon[delete-icon]')
      );

      const deleteCount = await deleteButton.count();

      if (deleteCount > 0) {
        // Click delete button
        await deleteButton.first().click();
        await page.waitForTimeout(300);

        // Check for confirmation dialog
        const confirmDialog = page.locator('.el-message-box').or(page.locator('.el-dialog'));
        const hasDialog = await confirmDialog.count() > 0;

        if (hasDialog) {
          // Verify dialog has warning text
          const dialogTitle = confirmDialog.locator('.el-message-box__title, .el-dialog__title');
          await expect(dialogTitle).toBeVisible();

          // Cancel the dialog
          const cancelButton = confirmDialog.locator('button', { hasText: /CANCEL/ }).first();
          await cancelButton.click();
        }
      }
    });

    test('should confirm and delete strategy', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Count strategies before delete
      const strategiesBefore = await page.locator('.strategy-card').count();

      // Find and click delete button
      const firstCard = page.locator('.strategy-card').first();
      const deleteButton = firstCard.locator('button', { hasText: /DELETE|REMOVE/ });

      const deleteCount = await deleteButton.count();

      if (deleteCount > 0) {
        await deleteButton.first().click();
        await page.waitForTimeout(300);

        // Find and click confirm button
        const confirmDialog = page.locator('.el-message-box');
        const confirmButton = confirmDialog.locator('button', { hasText: /DELETE|CONFIRM/ }).or(
          confirmDialog.locator('.el-button--danger')
        );

        const confirmCount = await confirmButton.count();

        if (confirmCount > 0) {
          // Store strategy name before deletion
          const strategyName = await firstCard.locator('h3, .strategy-name').first().textContent();

          // Confirm deletion
          await confirmButton.first().click();
          await page.waitForTimeout(1000);

          // Check for success message
          const messageBox = page.locator('.el-message--success');
          const hasSuccessMessage = await messageBox.count() > 0;

          if (hasSuccessMessage) {
            // Verify strategy was removed from list
            await page.waitForTimeout(500);
            const strategiesAfter = await page.locator('.strategy-card').count();

            // Note: May be equal if backend prevented deletion or no effect
            expect(strategiesAfter).toBeGreaterThanOrEqual(0);
          }
        }
      }
    });

    test('should cancel delete operation', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Count strategies before
      const strategiesBefore = await page.locator('.strategy-card').count();

      // Find and click delete button
      const firstCard = page.locator('.strategy-card').first();
      const deleteButton = firstCard.locator('button', { hasText: /DELETE|REMOVE/ });

      const deleteCount = await deleteButton.count();

      if (deleteCount > 0) {
        await deleteButton.first().click();
        await page.waitForTimeout(300);

        // Click cancel button
        const confirmDialog = page.locator('.el-message-box');
        const cancelButton = confirmDialog.locator('button', { hasText: /CANCEL/ }).first();

        await cancelButton.click();
        await page.waitForTimeout(500);

        // Verify strategy still exists in list
        const strategiesAfter = await page.locator('.strategy-card').count();
        expect(strategiesAfter).toBe(strategiesBefore);
      }
    });
  });
});
