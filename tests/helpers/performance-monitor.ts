/**
 * Performance Monitoring Module
 *
 * Provides utilities for performance testing, monitoring, and profiling:
 * - Page load time measurement
 * - Core Web Vitals (CWV) tracking
 * - API response time measurement
 * - Performance budget validation
 * - Performance regression detection
 * - Memory usage monitoring
 */

import { Page } from '@playwright/test';
import { isPerformanceMonitoringEnabled } from './test-env';

/**
 * Performance metrics collected from page
 */
export interface PerformanceMetrics {
  // Navigation timing
  navigationStart: number;
  fetchStart: number;
  responseEnd: number;
  domContentLoadedEventEnd: number;
  loadEventEnd: number;

  // Computed metrics
  pageLoadTime: number; // loadEventEnd - fetchStart
  timeToFirstByte: number; // responseEnd - fetchStart
  domContentLoaded: number; // domContentLoadedEventEnd - fetchStart

  // Core Web Vitals
  largestContentfulPaint?: number;
  firstInputDelay?: number;
  cumulativeLayoutShift?: number;

  // API metrics
  apiResponseTimes: number[];
  averageApiResponseTime: number;
  maxApiResponseTime: number;
  minApiResponseTime: number;

  // Resource metrics
  resourceCount: number;
  totalResourceSize: number;
  averageResourceSize: number;

  // Custom metrics
  customMetrics?: Record<string, number>;
}

/**
 * Performance budget thresholds
 */
export interface PerformanceBudget {
  pageLoadTime: number; // ms
  timeToFirstByte: number; // ms
  domContentLoaded: number; // ms
  largestContentfulPaint?: number; // ms
  firstInputDelay?: number; // ms
  cumulativeLayoutShift?: number; // ms
  averageApiResponseTime?: number; // ms
}

/**
 * Performance test result
 */
export interface PerformanceResult {
  passed: boolean;
  metrics: PerformanceMetrics;
  budget: PerformanceBudget;
  violations: string[];
  summary: string;
}

/**
 * Capture comprehensive performance metrics from page
 *
 * Collects all available performance data including:
 * - Navigation timing (load times)
 * - Core Web Vitals (LCP, FID, CLS)
 * - Resource metrics
 * - API response times
 *
 * @param page - Playwright page object
 * @returns Performance metrics object
 *
 * @example
 * const metrics = await capturePerformanceMetrics(page);
 * console.log(`Page loaded in ${metrics.pageLoadTime}ms`);
 */
export async function capturePerformanceMetrics(page: Page): Promise<PerformanceMetrics> {
  if (!isPerformanceMonitoringEnabled()) {
    return getEmptyMetrics();
  }

  try {
    // Get navigation timing metrics
    const navigationMetrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (!nav) {
        return {
          navigationStart: 0,
          fetchStart: 0,
          responseEnd: 0,
          domContentLoadedEventEnd: 0,
          loadEventEnd: 0,
        };
      }

      return {
        navigationStart: nav.navigationStart,
        fetchStart: nav.fetchStart,
        responseEnd: nav.responseEnd,
        domContentLoadedEventEnd: nav.domContentLoadedEventEnd,
        loadEventEnd: nav.loadEventEnd,
      };
    });

    // Get Core Web Vitals
    const webVitals = await captureWebVitals(page);

    // Get resource metrics
    const resourceMetrics = await captureResourceMetrics(page);

    // Calculate derived metrics
    const pageLoadTime = navigationMetrics.loadEventEnd - navigationMetrics.fetchStart;
    const timeToFirstByte = navigationMetrics.responseEnd - navigationMetrics.fetchStart;
    const domContentLoaded =
      navigationMetrics.domContentLoadedEventEnd - navigationMetrics.fetchStart;

    return {
      ...navigationMetrics,
      pageLoadTime,
      timeToFirstByte,
      domContentLoaded,
      ...webVitals,
      ...resourceMetrics,
    };
  } catch (error) {
    console.error('Failed to capture performance metrics:', error);
    return getEmptyMetrics();
  }
}

/**
 * Capture Core Web Vitals (LCP, FID, CLS)
 *
 * @internal
 */
async function captureWebVitals(
  page: Page
): Promise<{
  largestContentfulPaint?: number;
  firstInputDelay?: number;
  cumulativeLayoutShift?: number;
}> {
  return page.evaluate(() => {
    let lcp: number | undefined;
    let fid: number | undefined;
    let cls: number | undefined;

    try {
      // Largest Contentful Paint
      const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
      if (lcpEntries.length > 0) {
        lcp = lcpEntries[lcpEntries.length - 1].startTime;
      }

      // First Input Delay (via PerformanceEventTiming)
      const entries = performance.getEntriesByType('first-input');
      if (entries.length > 0) {
        const firstInput = entries[0] as PerformanceEventTiming;
        fid = firstInput.processingEnd - firstInput.startTime;
      }

      // Cumulative Layout Shift
      const clsEntries = performance.getEntriesByType('layout-shift');
      let totalCLS = 0;
      clsEntries.forEach((entry: any) => {
        if (!entry.hadRecentInput) {
          totalCLS += entry.value;
        }
      });
      cls = totalCLS;
    } catch (error) {
      console.warn('Failed to capture Web Vitals:', error);
    }

    return {
      largestContentfulPaint: lcp,
      firstInputDelay: fid,
      cumulativeLayoutShift: cls,
    };
  });
}

/**
 * Capture resource metrics (count, size)
 *
 * @internal
 */
async function captureResourceMetrics(
  page: Page
): Promise<{
  apiResponseTimes: number[];
  averageApiResponseTime: number;
  maxApiResponseTime: number;
  minApiResponseTime: number;
  resourceCount: number;
  totalResourceSize: number;
  averageResourceSize: number;
}> {
  return page.evaluate(() => {
    const resources = performance.getEntriesByType('resource');

    // Separate API calls from other resources
    const apiResources = resources.filter(
      (r) => r.name.includes('/api/') || r.name.includes('http')
    );

    const apiResponseTimes = apiResources.map((r) => {
      const resource = r as PerformanceResourceTiming;
      return resource.responseEnd - resource.startTime;
    });

    const totalSize = resources.reduce((sum, r) => {
      const resource = r as PerformanceResourceTiming;
      return sum + (resource.transferSize || 0);
    }, 0);

    return {
      apiResponseTimes,
      averageApiResponseTime:
        apiResponseTimes.length > 0
          ? apiResponseTimes.reduce((a, b) => a + b, 0) / apiResponseTimes.length
          : 0,
      maxApiResponseTime: apiResponseTimes.length > 0 ? Math.max(...apiResponseTimes) : 0,
      minApiResponseTime: apiResponseTimes.length > 0 ? Math.min(...apiResponseTimes) : 0,
      resourceCount: resources.length,
      totalResourceSize: totalSize,
      averageResourceSize: resources.length > 0 ? totalSize / resources.length : 0,
    };
  });
}

/**
 * Measure page load time with natural loading
 *
 * @param page - Playwright page object
 * @param url - URL to navigate to
 * @returns Load time in milliseconds
 *
 * @example
 * const loadTime = await measurePageLoadTime(page, '/dashboard');
 * expect(loadTime).toBeLessThan(3000);
 */
export async function measurePageLoadTime(page: Page, url: string): Promise<number> {
  const startTime = Date.now();

  await page.goto(url, {
    waitUntil: 'networkidle',
  });

  const endTime = Date.now();
  return endTime - startTime;
}

/**
 * Measure specific action performance
 *
 * @param page - Playwright page object
 * @param action - Async function representing the action
 * @param description - Description of the action
 * @returns Time taken in milliseconds
 *
 * @example
 * const clickTime = await measureAction(page, async () => {
 *   await page.click('[data-testid="button"]');
 *   await page.waitForNavigation();
 * }, 'Click button and navigate');
 */
export async function measureAction(
  page: Page,
  action: () => Promise<void>,
  description?: string
): Promise<number> {
  const startTime = Date.now();

  try {
    await action();
  } catch (error) {
    if (description) {
      console.error(`Action failed: ${description}`, error);
    }
    throw error;
  }

  const endTime = Date.now();
  const duration = endTime - startTime;

  if (description) {
    console.log(`${description}: ${duration}ms`);
  }

  return duration;
}

/**
 * Validate performance against budget
 *
 * @param metrics - Performance metrics to validate
 * @param budget - Performance budget thresholds
 * @returns Performance result with violations
 *
 * @example
 * const result = validatePerformanceBudget(metrics, {
 *   pageLoadTime: 3000,
 *   domContentLoaded: 2000,
 *   largestContentfulPaint: 2500,
 * });
 *
 * if (!result.passed) {
 *   console.log('Performance violations:');
 *   result.violations.forEach(v => console.log(`  - ${v}`));
 * }
 */
export function validatePerformanceBudget(
  metrics: PerformanceMetrics,
  budget: PerformanceBudget
): PerformanceResult {
  const violations: string[] = [];

  // Check page load time
  if (metrics.pageLoadTime > budget.pageLoadTime) {
    violations.push(
      `Page load time: ${metrics.pageLoadTime}ms exceeds budget of ${budget.pageLoadTime}ms`
    );
  }

  // Check time to first byte
  if (metrics.timeToFirstByte > budget.timeToFirstByte) {
    violations.push(
      `Time to first byte: ${metrics.timeToFirstByte}ms exceeds budget of ${budget.timeToFirstByte}ms`
    );
  }

  // Check DOM content loaded
  if (metrics.domContentLoaded > budget.domContentLoaded) {
    violations.push(
      `DOM content loaded: ${metrics.domContentLoaded}ms exceeds budget of ${budget.domContentLoaded}ms`
    );
  }

  // Check Core Web Vitals if specified
  if (
    budget.largestContentfulPaint &&
    metrics.largestContentfulPaint &&
    metrics.largestContentfulPaint > budget.largestContentfulPaint
  ) {
    violations.push(
      `LCP: ${metrics.largestContentfulPaint}ms exceeds budget of ${budget.largestContentfulPaint}ms`
    );
  }

  if (
    budget.firstInputDelay &&
    metrics.firstInputDelay &&
    metrics.firstInputDelay > budget.firstInputDelay
  ) {
    violations.push(
      `FID: ${metrics.firstInputDelay}ms exceeds budget of ${budget.firstInputDelay}ms`
    );
  }

  if (
    budget.cumulativeLayoutShift &&
    metrics.cumulativeLayoutShift &&
    metrics.cumulativeLayoutShift > budget.cumulativeLayoutShift
  ) {
    violations.push(
      `CLS: ${metrics.cumulativeLayoutShift} exceeds budget of ${budget.cumulativeLayoutShift}`
    );
  }

  // Check API response time if specified
  if (budget.averageApiResponseTime && metrics.averageApiResponseTime > 0) {
    if (metrics.averageApiResponseTime > budget.averageApiResponseTime) {
      violations.push(
        `Average API response: ${metrics.averageApiResponseTime}ms exceeds budget of ${budget.averageApiResponseTime}ms`
      );
    }
  }

  const passed = violations.length === 0;
  const summary = passed
    ? 'All performance metrics within budget ✓'
    : `${violations.length} performance violations detected`;

  return {
    passed,
    metrics,
    budget,
    violations,
    summary,
  };
}

/**
 * Get performance budgets for all pages
 *
 * @returns Map of page names to performance budgets
 *
 * @example
 * const budgets = getPerformanceBudgets();
 * const dashboardBudget = budgets.dashboard;
 */
export function getPerformanceBudgets(): Record<string, PerformanceBudget> {
  return {
    dashboard: {
      pageLoadTime: 3000,
      timeToFirstByte: 600,
      domContentLoaded: 2000,
      largestContentfulPaint: 2500,
      firstInputDelay: 100,
      cumulativeLayoutShift: 0.1,
      averageApiResponseTime: 1000,
    },
    market: {
      pageLoadTime: 3000,
      timeToFirstByte: 600,
      domContentLoaded: 2000,
      largestContentfulPaint: 2500,
      firstInputDelay: 100,
      cumulativeLayoutShift: 0.1,
      averageApiResponseTime: 1200,
    },
    stockDetail: {
      pageLoadTime: 3500,
      timeToFirstByte: 700,
      domContentLoaded: 2500,
      largestContentfulPaint: 3000,
      firstInputDelay: 100,
      cumulativeLayoutShift: 0.15,
      averageApiResponseTime: 1500,
    },
    trading: {
      pageLoadTime: 2500,
      timeToFirstByte: 500,
      domContentLoaded: 1800,
      largestContentfulPaint: 2000,
      firstInputDelay: 80,
      cumulativeLayoutShift: 0.1,
      averageApiResponseTime: 800,
    },
    settings: {
      pageLoadTime: 2000,
      timeToFirstByte: 400,
      domContentLoaded: 1500,
      largestContentfulPaint: 1800,
      firstInputDelay: 50,
      cumulativeLayoutShift: 0.05,
      averageApiResponseTime: 600,
    },
  };
}

/**
 * Log performance metrics in human-readable format
 *
 * @param metrics - Performance metrics
 *
 * @example
 * logPerformanceMetrics(metrics);
 * // Output:
 * // Page Load Time: 1234ms
 * // DOM Content Loaded: 890ms
 * // ...
 */
export function logPerformanceMetrics(metrics: PerformanceMetrics): void {
  console.log('\n═══ Performance Metrics ═══');
  console.log(`Page Load Time: ${metrics.pageLoadTime}ms`);
  console.log(`Time to First Byte: ${metrics.timeToFirstByte}ms`);
  console.log(`DOM Content Loaded: ${metrics.domContentLoaded}ms`);

  if (metrics.largestContentfulPaint) {
    console.log(`Largest Contentful Paint: ${metrics.largestContentfulPaint}ms`);
  }

  if (metrics.firstInputDelay) {
    console.log(`First Input Delay: ${metrics.firstInputDelay}ms`);
  }

  if (metrics.cumulativeLayoutShift) {
    console.log(`Cumulative Layout Shift: ${metrics.cumulativeLayoutShift}`);
  }

  console.log(`\nResources: ${metrics.resourceCount}`);
  console.log(`Total Size: ${(metrics.totalResourceSize / 1024).toFixed(2)}KB`);

  if (metrics.apiResponseTimes.length > 0) {
    console.log(
      `\nAPI Calls: ${metrics.apiResponseTimes.length} (avg: ${metrics.averageApiResponseTime.toFixed(0)}ms)`
    );
  }

  console.log('═══════════════════════════\n');
}

/**
 * Compare two performance results and detect regressions
 *
 * @param current - Current performance metrics
 * @param baseline - Baseline performance metrics
 * @param threshold - Maximum acceptable increase percentage (default: 10%)
 * @returns Array of detected regressions
 *
 * @example
 * const regressions = detectPerformanceRegression(currentMetrics, baselineMetrics, 5);
 * if (regressions.length > 0) {
 *   console.log('Performance regressions detected:');
 *   regressions.forEach(r => console.log(`  - ${r}`));
 * }
 */
export function detectPerformanceRegression(
  current: PerformanceMetrics,
  baseline: PerformanceMetrics,
  threshold: number = 10
): string[] {
  const regressions: string[] = [];
  const thresholdMultiplier = 1 + threshold / 100;

  if (current.pageLoadTime > baseline.pageLoadTime * thresholdMultiplier) {
    const increase = (
      ((current.pageLoadTime - baseline.pageLoadTime) / baseline.pageLoadTime) *
      100
    ).toFixed(1);
    regressions.push(`Page load time increased by ${increase}% (${current.pageLoadTime}ms)`);
  }

  if (current.domContentLoaded > baseline.domContentLoaded * thresholdMultiplier) {
    const increase = (
      ((current.domContentLoaded - baseline.domContentLoaded) / baseline.domContentLoaded) *
      100
    ).toFixed(1);
    regressions.push(`DOM content loaded increased by ${increase}% (${current.domContentLoaded}ms)`);
  }

  if (
    current.averageApiResponseTime > 0 &&
    baseline.averageApiResponseTime > 0 &&
    current.averageApiResponseTime > baseline.averageApiResponseTime * thresholdMultiplier
  ) {
    const increase = (
      ((current.averageApiResponseTime - baseline.averageApiResponseTime) /
        baseline.averageApiResponseTime) *
      100
    ).toFixed(1);
    regressions.push(
      `Average API response time increased by ${increase}% (${current.averageApiResponseTime.toFixed(0)}ms)`
    );
  }

  return regressions;
}

/**
 * Get empty performance metrics (for error handling)
 *
 * @internal
 */
function getEmptyMetrics(): PerformanceMetrics {
  return {
    navigationStart: 0,
    fetchStart: 0,
    responseEnd: 0,
    domContentLoadedEventEnd: 0,
    loadEventEnd: 0,
    pageLoadTime: 0,
    timeToFirstByte: 0,
    domContentLoaded: 0,
    apiResponseTimes: [],
    averageApiResponseTime: 0,
    maxApiResponseTime: 0,
    minApiResponseTime: 0,
    resourceCount: 0,
    totalResourceSize: 0,
    averageResourceSize: 0,
  };
}
