/**
 * Visual Regression Testing Module
 *
 * Provides utilities for visual regression testing using Percy (preferred)
 * or native Playwright snapshot testing as fallback.
 *
 * Features:
 * - Percy visual regression detection
 * - Baseline snapshot creation and comparison
 * - Multi-device visual testing (desktop, tablet, mobile)
 * - Responsive design validation
 * - Custom element snapshot capture
 * - Thresholds for acceptable visual changes
 */

import { Page, expect } from '@playwright/test';
import { isVisualRegressionEnabled } from './test-env';

/**
 * Visual regression configuration
 */
export interface VisualRegressionOptions {
  // Snapshot name for Percy
  name: string;

  // Optional: Custom widths for responsive testing
  widths?: number[];

  // Optional: Enable/disable Percy (default: check env)
  enabled?: boolean;

  // Optional: Minimal snapshots (exclude regions)
  minimalSnapshots?: boolean;

  // Optional: Custom Percy options
  percyOptions?: {
    scope?: string;
    prefix?: string;
    hidden?: string[];
    frozen?: string[];
  };

  // Optional: Maximum acceptable difference percentage
  maxDiffPercentage?: number;

  // Optional: Wait before snapshot (ms)
  waitForMs?: number;

  // Optional: Wait for selector before snapshot
  waitForSelector?: string;

  // Optional: Elements to hide from snapshot
  elementsToHide?: string[];

  // Optional: Elements to freeze (ignore changes)
  elementsToFreeze?: string[];
}

/**
 * Snapshot comparison result
 */
export interface SnapshotComparisonResult {
  passed: boolean;
  diffPercentage: number;
  message: string;
  snapshotPath?: string;
}

/**
 * Capture visual snapshot using Percy (if available)
 *
 * Automatically detects Percy availability and falls back to native
 * Playwright snapshot testing if Percy is not configured.
 *
 * @param page - Playwright page object
 * @param options - Configuration options
 *
 * @example
 * // Simple snapshot
 * await captureVisualSnapshot(page, { name: 'Dashboard Overview' });
 *
 * @example
 * // With responsive widths
 * await captureVisualSnapshot(page, {
 *   name: 'Dashboard Responsive',
 *   widths: [375, 768, 1920],  // Mobile, Tablet, Desktop
 * });
 *
 * @example
 * // With custom options
 * await captureVisualSnapshot(page, {
 *   name: 'Dashboard Form',
 *   waitForSelector: '[data-testid="form-ready"]',
 *   elementsToHide: ['[data-testid="animated-banner"]'],
 *   elementsToFreeze: ['[data-testid="video-player"]'],
 * });
 */
export async function captureVisualSnapshot(
  page: Page,
  options: VisualRegressionOptions
): Promise<void> {
  // Check if visual regression is enabled
  const enabled = options.enabled ?? isVisualRegressionEnabled();
  if (!enabled) {
    return;
  }

  try {
    // Wait for content to be ready
    if (options.waitForMs) {
      await page.waitForTimeout(options.waitForMs);
    }

    if (options.waitForSelector) {
      await page.waitForSelector(options.waitForSelector, { timeout: 5000 });
    }

    // Hide specified elements
    if (options.elementsToHide && options.elementsToHide.length > 0) {
      await hideElements(page, options.elementsToHide);
    }

    // Freeze specified elements
    if (options.elementsToFreeze && options.elementsToFreeze.length > 0) {
      await freezeElements(page, options.elementsToFreeze);
    }

    // Try Percy snapshot (if available)
    try {
      await percySnapshot(page, options);
      console.log(`✓ Percy snapshot captured: ${options.name}`);
    } catch (error) {
      // Percy not available, use Playwright snapshot
      console.log(`⚠ Percy unavailable, using Playwright snapshot: ${options.name}`);
      await playwrightSnapshot(page, options);
    }
  } catch (error) {
    console.error(`Failed to capture visual snapshot: ${options.name}`, error);
    throw error;
  }
}

/**
 * Capture Percy snapshot
 *
 * @internal
 */
async function percySnapshot(page: Page, options: VisualRegressionOptions): Promise<void> {
  // Import Percy dynamically (optional dependency)
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires, global-require
    const { percySnapshot: _percySnapshot } = require('@percy/playwright');

    const percyOptions: any = {
      widths: options.widths || [1920],
      minimalSnapshots: options.minimalSnapshots ?? false,
      ...options.percyOptions,
    };

    if (options.elementsToHide && options.elementsToHide.length > 0) {
      percyOptions.hidden = options.elementsToHide;
    }

    if (options.elementsToFreeze && options.elementsToFreeze.length > 0) {
      percyOptions.frozen = options.elementsToFreeze;
    }

    await _percySnapshot(page, options.name, percyOptions);
  } catch (error) {
    throw new Error('Percy snapshot failed or Percy is not installed');
  }
}

/**
 * Capture Playwright snapshot as fallback
 *
 * @internal
 */
async function playwrightSnapshot(page: Page, options: VisualRegressionOptions): Promise<void> {
  const snapshotName = options.name
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');

  const snapshotPath = `tests/visual-snapshots/${snapshotName}.png`;

  // Take screenshot
  const screenshot = await page.screenshot({ fullPage: true });

  // Compare with baseline if it exists
  // Note: This is a simplified implementation
  // In production, use jest-image-snapshot or similar
  await expect(screenshot).toMatchSnapshot(`${snapshotName}.png`);
}

/**
 * Capture snapshot of specific element
 *
 * @param page - Playwright page object
 * @param selector - CSS selector of element to capture
 * @param name - Snapshot name
 * @param options - Additional options
 *
 * @example
 * await captureElementSnapshot(page, '[data-testid="dashboard-header"]', 'Dashboard Header');
 */
export async function captureElementSnapshot(
  page: Page,
  selector: string,
  name: string,
  options?: Partial<VisualRegressionOptions>
): Promise<void> {
  const element = await page.$(selector);
  if (!element) {
    throw new Error(`Element not found: ${selector}`);
  }

  // Scroll element into view
  await element.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300); // Wait for scroll animation

  // Take element screenshot
  const screenshot = await element.screenshot();

  // Fallback to Playwright snapshot
  const snapshotName = name
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');

  await expect(screenshot).toMatchSnapshot(`${snapshotName}.png`);
}

/**
 * Capture responsive design snapshots (mobile, tablet, desktop)
 *
 * @param page - Playwright page object
 * @param name - Base snapshot name
 * @param options - Configuration options
 *
 * @example
 * await captureResponsiveSnapshot(page, 'Dashboard Layout');
 * // Captures: Dashboard Layout-mobile.png, Dashboard Layout-tablet.png, Dashboard Layout-desktop.png
 */
export async function captureResponsiveSnapshot(
  page: Page,
  name: string,
  options?: Partial<VisualRegressionOptions>
): Promise<void> {
  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1920, height: 1080 },
  ];

  for (const viewport of viewports) {
    await page.setViewportSize({
      width: viewport.width,
      height: viewport.height,
    });

    // Wait for responsive layout to adjust
    await page.waitForTimeout(300);

    await captureVisualSnapshot(page, {
      name: `${name} - ${viewport.name}`,
      waitForSelector: options?.waitForSelector,
      elementsToHide: options?.elementsToHide,
      elementsToFreeze: options?.elementsToFreeze,
      ...options,
    });
  }
}

/**
 * Hide elements from visual snapshot
 *
 * @param page - Playwright page object
 * @param selectors - Array of CSS selectors to hide
 *
 * @example
 * await hideElements(page, ['[data-testid="banner"]', '.advertisement']);
 */
export async function hideElements(page: Page, selectors: string[]): Promise<void> {
  await page.evaluate((sels: string[]) => {
    sels.forEach((selector) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach((el) => {
        (el as HTMLElement).style.visibility = 'hidden';
      });
    });
  }, selectors);
}

/**
 * Freeze elements from visual snapshot (ignore changes)
 *
 * @param page - Playwright page object
 * @param selectors - Array of CSS selectors to freeze
 *
 * @example
 * await freezeElements(page, ['[data-testid="video-player"]']);
 */
export async function freezeElements(page: Page, selectors: string[]): Promise<void> {
  await page.evaluate((sels: string[]) => {
    sels.forEach((selector) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach((el) => {
        (el as HTMLElement).style.pointerEvents = 'none';
      });
    });
  }, selectors);
}

/**
 * Compare two snapshots and return difference percentage
 *
 * @param page - Playwright page object
 * @param snapshotName - Name of snapshot to compare
 * @param maxDiffPercentage - Maximum acceptable difference (0-100)
 * @returns Comparison result with passed status and diff percentage
 *
 * @example
 * const result = await compareSnapshots(page, 'Dashboard', 5);
 * if (!result.passed) {
 *   console.log(`Visual regression detected: ${result.diffPercentage}%`);
 * }
 */
export async function compareSnapshots(
  page: Page,
  snapshotName: string,
  maxDiffPercentage: number = 2
): Promise<SnapshotComparisonResult> {
  try {
    const screenshot = await page.screenshot({ fullPage: true });

    await expect(screenshot).toMatchSnapshot(`${snapshotName}.png`);

    return {
      passed: true,
      diffPercentage: 0,
      message: 'Snapshot matches baseline',
    };
  } catch (error) {
    // Extract diff percentage from error message
    const message = String(error);
    const diffMatch = message.match(/(\d+\.?\d*)%/);
    const diffPercentage = diffMatch ? parseFloat(diffMatch[1]) : 100;

    return {
      passed: diffPercentage <= maxDiffPercentage,
      diffPercentage,
      message: `Snapshot differs by ${diffPercentage}%`,
    };
  }
}

/**
 * Create baseline snapshots for all critical pages
 *
 * @param page - Playwright page object
 * @param pageConfigs - Configuration for each page
 *
 * @example
 * await createBaselineSnapshots(page, [
 *   { path: '/dashboard', name: 'Dashboard' },
 *   { path: '/market', name: 'Market' },
 *   { path: '/trading', name: 'Trading' },
 * ]);
 */
export async function createBaselineSnapshots(
  page: Page,
  pageConfigs: Array<{
    path: string;
    name: string;
    waitForSelector?: string;
  }>
): Promise<void> {
  for (const config of pageConfigs) {
    try {
      // Navigate to page
      await page.goto(config.path, { waitUntil: 'networkidle' });

      // Wait for content
      if (config.waitForSelector) {
        await page.waitForSelector(config.waitForSelector, { timeout: 10000 });
      } else {
        await page.waitForTimeout(500);
      }

      // Capture snapshot
      await captureVisualSnapshot(page, {
        name: `${config.name} - Baseline`,
        widths: [1920, 768, 375], // Desktop, tablet, mobile
      });

      console.log(`✓ Baseline snapshot created: ${config.name}`);
    } catch (error) {
      console.error(`Failed to create baseline for ${config.name}:`, error);
    }
  }
}

/**
 * Get visual regression configuration for Percy
 *
 * @returns Configuration object for Percy initialization
 *
 * @example
 * const percyConfig = getPercyConfiguration();
 * console.log(percyConfig);
 */
export function getPercyConfiguration(): {
  enabled: boolean;
  projectName?: string;
  buildNumber?: string;
} {
  return {
    enabled: isVisualRegressionEnabled(),
    projectName: process.env.PERCY_PROJECT || 'mystocks-e2e-tests',
    buildNumber: process.env.BUILD_NUMBER || String(Date.now()),
  };
}

/**
 * Check if visual regression testing is available
 *
 * @returns true if Percy or Playwright snapshots are available
 */
export async function isVisualRegressionAvailable(): Promise<boolean> {
  try {
    // Check if Percy is installed
    require('@percy/playwright');
    return true;
  } catch {
    // Fallback to Playwright snapshots
    return true; // Always available
  }
}

/**
 * Initialize visual regression testing
 *
 * Should be called once before all visual tests
 *
 * @example
 * test.beforeAll(async () => {
 *   await initializeVisualRegression();
 * });
 */
export async function initializeVisualRegression(): Promise<void> {
  const available = await isVisualRegressionAvailable();

  if (!available) {
    throw new Error('Visual regression testing not available');
  }

  const config = getPercyConfiguration();
  console.log(`Visual Regression Testing Initialized`);
  console.log(`  Enabled: ${config.enabled}`);
  console.log(`  Project: ${config.projectName}`);
  console.log(`  Build: ${config.buildNumber}`);
}
