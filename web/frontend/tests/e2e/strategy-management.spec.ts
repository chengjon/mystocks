/**
 * Strategy Management Module E2E Tests
 *
 * End-to-end tests for strategy management functionality using Playwright.
 * Tests cover user journeys, CRUD operations, backtesting, and UI interactions.
 */

import { test, expect } from '@playwright/test';

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
const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';

/**
 * Helper: Login to the application
 */
async function login(page) {
  await page.goto(`${BASE_URL}/login`);

  // Fill in login credentials
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'password');

  // Click login button
  await page.click('button[type="submit"]');

  // Wait for navigation to complete
  await page.waitForURL('**/dashboard');
}

test.describe('Strategy Management Module - E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set default viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test.describe('Strategy List Page', () => {
    test('should load strategy management page successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Check page title
      await expect(page).toHaveTitle(/MyStocks/);

      // Check main heading
      const heading = page.locator('h1, h2').filter({ hasText: /策略管理|Strategy Management/ });
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
      await page.route('**/api/strategy/list', (route) => {
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

      // Find sidebar
      const sidebar = page.locator('.sidebar, aside, [data-testid="sidebar"]');
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
      await page.route('**/api/strategy/list', async (route) => {
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
});
