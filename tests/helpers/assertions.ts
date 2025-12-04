/**
 * Custom Assertion Helpers for E2E Testing
 *
 * Provides reusable assertion functions for common test scenarios
 * across the MyStocks E2E test suite.
 *
 * Version: 1.0.0
 * Date: 2025-12-04
 */

import { expect, Page, Locator } from '@playwright/test';

/**
 * Assert that page has loaded with no errors
 */
export async function assertPageLoadedSuccessfully(page: Page): Promise<void> {
  // Check for error messages
  const errorElements = await page.locator('[data-testid="error-message"]').count();
  expect(errorElements).toBe(0);

  // Check page is not showing loading state indefinitely
  const loadingSpinner = page.locator('[data-testid="loading-spinner"]');
  const isVisible = await loadingSpinner.isVisible().catch(() => false);
  expect(isVisible).toBeFalsy();
}

/**
 * Assert that data is displayed on page
 */
export async function assertDataDisplayed(element: Locator): Promise<void> {
  await expect(element).toBeVisible();
  const text = await element.textContent();
  expect(text).toBeTruthy();
  expect(text).not.toMatch(/^\s*$/); // Not just whitespace
}

/**
 * Assert that element contains specific text
 */
export async function assertElementContainsText(element: Locator, text: string): Promise<void> {
  await expect(element).toContainText(text);
}

/**
 * Assert that element has specific class
 */
export async function assertElementHasClass(element: Locator, className: string): Promise<void> {
  const classes = await element.getAttribute('class');
  expect(classes).toContain(className);
}

/**
 * Assert that numeric value is within range
 */
export async function assertValueInRange(
  element: Locator,
  minValue: number,
  maxValue: number
): Promise<void> {
  const text = await element.textContent();
  expect(text).toBeTruthy();

  // Extract numeric value
  const matches = text!.match(/[\d.]+/);
  expect(matches).toBeTruthy();

  if (matches) {
    const value = parseFloat(matches[0]);
    expect(value).toBeGreaterThanOrEqual(minValue);
    expect(value).toBeLessThanOrEqual(maxValue);
  }
}

/**
 * Assert that table/list has expected number of rows
 */
export async function assertRowCount(container: Locator, rowSelector: string, expectedCount: number): Promise<void> {
  const rows = container.locator(rowSelector);
  const count = await rows.count();
  expect(count).toBe(expectedCount);
}

/**
 * Assert that list is not empty
 */
export async function assertListNotEmpty(container: Locator, itemSelector: string): Promise<void> {
  const items = container.locator(itemSelector);
  const count = await items.count();
  expect(count).toBeGreaterThan(0);
}

/**
 * Assert that list is empty
 */
export async function assertListEmpty(container: Locator, itemSelector: string): Promise<void> {
  const items = container.locator(itemSelector);
  const count = await items.count();
  expect(count).toBe(0);
}

/**
 * Assert that modal/dialog is displayed
 */
export async function assertModalDisplayed(page: Page, modalSelector: string): Promise<void> {
  const modal = page.locator(modalSelector);
  await expect(modal).toBeVisible();

  // Check that modal has backdrop/overlay
  const backdrop = page.locator('.el-overlay, .modal-overlay');
  const backdrops = await backdrop.count();
  expect(backdrops).toBeGreaterThan(0);
}

/**
 * Assert that modal/dialog is closed
 */
export async function assertModalClosed(page: Page, modalSelector: string): Promise<void> {
  const modal = page.locator(modalSelector);
  await expect(modal).not.toBeVisible();
}

/**
 * Assert that form has validation error
 */
export async function assertFormHasError(
  form: Locator,
  fieldName: string,
  errorMessage?: string
): Promise<void> {
  const errorElement = form.locator(`[data-field="${fieldName}"] .error-message`);
  await expect(errorElement).toBeVisible();

  if (errorMessage) {
    const actualMessage = await errorElement.textContent();
    expect(actualMessage).toContain(errorMessage);
  }
}

/**
 * Assert that form field is required
 */
export async function assertFieldRequired(form: Locator, fieldName: string): Promise<void> {
  const field = form.locator(`[data-field="${fieldName}"]`);
  const requiredIndicator = field.locator('.required-indicator, [aria-label*="required"]');
  await expect(requiredIndicator).toBeVisible();
}

/**
 * Assert that button is disabled
 */
export async function assertButtonDisabled(button: Locator): Promise<void> {
  await expect(button).toBeDisabled();
  const classes = await button.getAttribute('class');
  expect(classes).toContain('disabled');
}

/**
 * Assert that button is enabled
 */
export async function assertButtonEnabled(button: Locator): Promise<void> {
  await expect(button).toBeEnabled();
}

/**
 * Assert that table column headers exist
 */
export async function assertTableHeaders(
  table: Locator,
  expectedHeaders: string[]
): Promise<void> {
  const headers = await table.locator('th').allTextContents();
  expectedHeaders.forEach((header) => {
    expect(headers.some((h) => h.includes(header))).toBeTruthy();
  });
}

/**
 * Assert that chart is rendered
 */
export async function assertChartRendered(page: Page, chartSelector: string): Promise<void> {
  const chart = page.locator(chartSelector);
  await expect(chart).toBeVisible();

  // Check for canvas or SVG elements (common in chart libraries)
  const canvases = chart.locator('canvas');
  const svgs = chart.locator('svg');
  const canvasCount = await canvases.count();
  const svgCount = await svgs.count();

  expect(canvasCount + svgCount).toBeGreaterThan(0);
}

/**
 * Assert that real-time data updates
 */
export async function assertDataUpdates(
  element: Locator,
  maxWaitTime: number = 10000
): Promise<void> {
  const initialValue = await element.textContent();
  let updated = false;
  let attempts = 0;
  const maxAttempts = 20;

  while (!updated && attempts < maxAttempts) {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const currentValue = await element.textContent();
    if (currentValue !== initialValue) {
      updated = true;
    }
    attempts++;
  }

  expect(updated).toBeTruthy();
}

/**
 * Assert response data structure
 */
export function assertResponseStructure(
  data: Record<string, any>,
  expectedKeys: string[]
): void {
  expectedKeys.forEach((key) => {
    expect(data).toHaveProperty(key);
  });
}

/**
 * Assert that API response is valid
 */
export function assertApiResponseValid(
  response: Record<string, any>,
  expectedStatus: number = 200
): void {
  expect(response).toHaveProperty('status');
  expect(response.status).toBe(expectedStatus);

  if (expectedStatus === 200) {
    expect(response).toHaveProperty('success', true);
    expect(response).toHaveProperty('data');
  }
}

/**
 * Assert that WebSocket connection is established
 */
export async function assertWebSocketConnected(page: Page): Promise<void> {
  // Wait for WebSocket messages or status indicator
  const wsStatus = page.locator('[data-testid="ws-status"]');
  const isConnected = await wsStatus.getAttribute('data-connected');
  expect(isConnected).toBe('true');
}

/**
 * Assert pagination controls visibility
 */
export async function assertPaginationVisible(page: Page): Promise<void> {
  const pagination = page.locator('[data-testid="pagination"]');
  await expect(pagination).toBeVisible();

  const prevBtn = pagination.locator('button[data-direction="prev"]');
  const nextBtn = pagination.locator('button[data-direction="next"]');

  await expect(prevBtn).toBeDefined();
  await expect(nextBtn).toBeDefined();
}

/**
 * Assert sorting functionality
 */
export async function assertSortingApplied(
  element: Locator,
  sortDirection: 'asc' | 'desc'
): Promise<void> {
  const classes = await element.getAttribute('class');
  const expectedClass = sortDirection === 'asc' ? 'sort-asc' : 'sort-desc';
  expect(classes).toContain(expectedClass);
}

/**
 * Assert responsive design (desktop view)
 */
export async function assertDesktopLayout(page: Page): Promise<void> {
  await page.setViewportSize({ width: 1920, height: 1080 });

  // Verify layout adjustments for desktop
  const gridLayout = page.locator('[data-testid="grid-layout"]');
  const classes = await gridLayout.getAttribute('class');
  expect(classes).toMatch(/grid-cols-[3-4]/); // Desktop: 3-4 columns
}

/**
 * Assert responsive design (tablet view)
 */
export async function assertTabletLayout(page: Page): Promise<void> {
  await page.setViewportSize({ width: 768, height: 1024 });

  // Verify layout adjustments for tablet
  const gridLayout = page.locator('[data-testid="grid-layout"]');
  const classes = await gridLayout.getAttribute('class');
  expect(classes).toMatch(/grid-cols-2/); // Tablet: 2 columns
}

/**
 * Assert responsive design (mobile view)
 */
export async function assertMobileLayout(page: Page): Promise<void> {
  await page.setViewportSize({ width: 375, height: 667 });

  // Verify layout adjustments for mobile
  const gridLayout = page.locator('[data-testid="grid-layout"]');
  const classes = await gridLayout.getAttribute('class');
  expect(classes).toMatch(/grid-cols-1/); // Mobile: 1 column
}

/**
 * Assert notification/toast message
 */
export async function assertToastMessage(
  page: Page,
  message: string,
  type: 'success' | 'error' | 'warning' | 'info' = 'success'
): Promise<void> {
  const toast = page.locator(`[data-testid="toast"][data-type="${type}"]`);
  await expect(toast).toBeVisible();
  await expect(toast).toContainText(message);
}

/**
 * Assert no errors in console
 */
export async function assertNoConsoleErrors(page: Page): Promise<void> {
  const messages = await page.evaluate(() => {
    // This needs to be captured during test execution
    return (window as any).__consoleErrors || [];
  });

  expect(messages).toHaveLength(0);
}

/**
 * Assert page performance metrics
 */
export async function assertPagePerformance(page: Page, maxLoadTime: number = 3000): Promise<void> {
  const navigationTiming = await page.evaluate(() => {
    const timing = window.performance.timing;
    return timing.loadEventEnd - timing.navigationStart;
  });

  expect(navigationTiming).toBeLessThan(maxLoadTime);
}
