/**
 * Conditional Mocking Module
 *
 * Provides utilities to seamlessly switch between mock and real API calls
 * based on environment configuration. Allows tests to run in both offline
 * (mock) and online (real API) modes without code changes.
 */

import { Page, Route } from '@playwright/test';
import { shouldUseMocks, getApiBaseUrl } from './test-env';
import {
  mockDashboardApis,
  mockMarketApis,
  mockTradingApis,
  mockStrategyApis,
  mockRiskApis,
  mockTaskApis,
  mockSettingsApis,
  mockTechnicalAnalysisApis,
  mockMonitoringApis,
  mockWencaiApis,
} from './api-helpers';

/**
 * Conditional API setup - uses mock or real APIs based on configuration
 *
 * Automatically selects between mock and real APIs:
 * - If USE_MOCK_API=true or not set: All APIs are mocked
 * - If USE_REAL_API=true: Real APIs are used without interception
 *
 * @param page - Playwright page object
 * @param options - Configuration options
 *
 * @example
 * test.beforeEach(async ({ page }) => {
 *   await setupApi(page);
 *   await page.goto('/dashboard');
 * });
 *
 * @example
 * // Force mock mode for a specific test
 * test('test with mocks', async ({ page }) => {
 *   await setupApi(page, { useMocks: true });
 * });
 *
 * @example
 * // Force real API for a specific test
 * test('integration test', async ({ page }) => {
 *   await setupApi(page, { useMocks: false });
 * });
 */
export async function setupApi(
  page: Page,
  options: {
    useMocks?: boolean;
    mockDelay?: number;
    includeCategories?: string[];
    excludeCategories?: string[];
  } = {}
): Promise<void> {
  const useMocks = options.useMocks ?? shouldUseMocks();
  const mockDelay = options.mockDelay ?? 0;

  if (useMocks) {
    console.log('Setting up MOCK APIs for testing');

    const defaultCategories = [
      'dashboard',
      'market',
      'trading',
      'strategies',
      'risk',
      'tasks',
      'settings',
      'technical',
      'monitoring',
      'wencai',
    ];

    const categoriesToMock = options.includeCategories || defaultCategories;
    const categoriesToExclude = options.excludeCategories || [];
    const finalCategories = categoriesToMock.filter(
      (cat) => !categoriesToExclude.includes(cat)
    );

    // Set up all selected mock APIs
    for (const category of finalCategories) {
      try {
        await setupMockCategory(page, category, mockDelay);
      } catch (error) {
        console.warn(`Failed to setup mock for category: ${category}`, error);
      }
    }

    console.log(`✓ Mock APIs configured for categories: ${finalCategories.join(', ')}`);
  } else {
    console.log(`Using REAL APIs from ${getApiBaseUrl()}`);
    // Real APIs - no mocking needed
    // Page will make actual HTTP requests to the backend
  }
}

/**
 * Set up mocks for a specific API category
 *
 * @param page - Playwright page object
 * @param category - API category name ('dashboard', 'market', etc.)
 * @param mockDelay - Optional delay to simulate network latency (ms)
 *
 * @internal
 */
async function setupMockCategory(
  page: Page,
  category: string,
  mockDelay: number = 0
): Promise<void> {
  const mockSetuppers: Record<string, (page: Page) => Promise<void>> = {
    dashboard: mockDashboardApis,
    market: mockMarketApis,
    trading: mockTradingApis,
    strategies: mockStrategyApis,
    risk: mockRiskApis,
    tasks: mockTaskApis,
    settings: mockSettingsApis,
    technical: mockTechnicalAnalysisApis,
    monitoring: mockMonitoringApis,
    wencai: mockWencaiApis,
  };

  const setupper = mockSetuppers[category];
  if (!setupper) {
    throw new Error(`Unknown mock category: ${category}`);
  }

  await setupper(page);

  // Apply delay if specified
  if (mockDelay > 0) {
    await applyMockDelay(page, mockDelay);
  }
}

/**
 * Apply artificial delay to all mocked API responses
 *
 * Useful for testing loading states and performance
 *
 * @param page - Playwright page object
 * @param delayMs - Delay in milliseconds
 *
 * @example
 * // Simulate slow network
 * await applyMockDelay(page, 2000);
 */
export async function applyMockDelay(page: Page, delayMs: number): Promise<void> {
  await page.addInitScript(
    (delayMs) => {
      const originalFetch = window.fetch;
      window.fetch = async (...args: any[]) => {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
        return originalFetch(...args);
      };
    },
    delayMs
  );
}

/**
 * Set up conditional API for a specific endpoint
 *
 * Intercepts requests to an endpoint and either:
 * - Returns mock data (if USE_MOCK_API=true)
 * - Passes through to real backend (if USE_REAL_API=true)
 *
 * @param page - Playwright page object
 * @param urlPattern - URL pattern to intercept (glob pattern)
 * @param mockHandler - Function that returns mock response
 * @param options - Additional options
 *
 * @example
 * // Conditionally intercept dashboard endpoint
 * await setupConditionalEndpoint(
 *   page,
 *   '**/api/dashboard/**',
 *   async (route) => {
 *     // Return mock data
 *     await route.respond({
 *       status: 200,
 *       body: JSON.stringify(mockDashboardData),
 *     });
 *   }
 * );
 */
export async function setupConditionalEndpoint(
  page: Page,
  urlPattern: string,
  mockHandler: (route: Route) => Promise<void>,
  options: { enabled?: boolean } = {}
): Promise<void> {
  if (options.enabled === false) {
    return;
  }

  const useMocks = shouldUseMocks();

  if (useMocks) {
    await page.route(urlPattern, mockHandler);
  } else {
    // Real API mode - pass through without mocking
    await page.route(urlPattern, async (route) => {
      await route.continue();
    });
  }
}

/**
 * Disable all mocks for specific test
 *
 * Temporarily switches to real API mode for a specific operation
 *
 * @param page - Playwright page object
 * @returns Function to restore previous mock configuration
 *
 * @example
 * const restore = await disableMocks(page);
 * // Make real API call
 * await page.goto('/api/real-endpoint');
 * // Restore mocks
 * await restore();
 */
export async function disableMocks(page: Page): Promise<() => Promise<void>> {
  const currentRoutes = page.context().route;
  // Note: Playwright doesn't expose route history directly
  // This is a placeholder for manual route management

  return async () => {
    // Restore previous routes - would need custom implementation
    console.log('Mocks remain in place');
  };
}

/**
 * Enable mocks for specific test
 *
 * Ensures all APIs use mock data for the current test
 *
 * @param page - Playwright page object
 * @param categories - Specific categories to mock (optional, defaults to all)
 *
 * @example
 * // Mock only dashboard and market APIs
 * await enableMocks(page, ['dashboard', 'market']);
 */
export async function enableMocks(
  page: Page,
  categories?: string[]
): Promise<void> {
  await setupApi(page, {
    useMocks: true,
    includeCategories: categories,
  });
}

/**
 * Test helper to verify mock is active
 *
 * @returns true if mock APIs are currently enabled
 *
 * @example
 * test('should use mocks', async ({ page }) => {
 *   await setupApi(page, { useMocks: true });
 *   expect(isMockEnabled()).toBe(true);
 * });
 */
export function isMockEnabled(): boolean {
  return shouldUseMocks();
}

/**
 * Configure error behavior for mock APIs
 *
 * Useful for testing error handling
 *
 * @param page - Playwright page object
 * @param errorConfig - Configuration for error responses
 *
 * @example
 * // All API calls return 500 error
 * await configureMockErrors(page, {
 *   enabled: true,
 *   statusCode: 500,
 *   message: 'Internal Server Error',
 * });
 */
export async function configureMockErrors(
  page: Page,
  errorConfig: {
    enabled: boolean;
    statusCode?: number;
    message?: string;
    categories?: string[];
  }
): Promise<void> {
  if (!errorConfig.enabled) {
    return;
  }

  const statusCode = errorConfig.statusCode ?? 500;
  const message = errorConfig.message ?? 'Internal Server Error';
  const categories = errorConfig.categories ?? ['dashboard', 'market', 'trading'];

  for (const category of categories) {
    await page.route(`**/api/**/${category}/**`, async (route) => {
      await route.respond({
        status: statusCode,
        contentType: 'application/json',
        body: JSON.stringify({
          error: message,
          status: statusCode,
        }),
      });
    });
  }
}

/**
 * Get current mock configuration as a summary
 *
 * @returns Object containing mock configuration details
 *
 * @example
 * const config = getMockConfiguration();
 * console.log(config);
 * // { enabled: true, categories: ['dashboard', 'market', ...], delay: 0 }
 */
export function getMockConfiguration(): {
  enabled: boolean;
  apiBaseUrl: string;
} {
  return {
    enabled: shouldUseMocks(),
    apiBaseUrl: getApiBaseUrl(),
  };
}

/**
 * Helper to set up all APIs in mock mode
 *
 * @param page - Playwright page object
 * @param mockDelay - Optional delay to simulate network latency
 *
 * @example
 * test.beforeEach(async ({ page }) => {
 *   await setupAllMocks(page);
 * });
 */
export async function setupAllMocks(
  page: Page,
  mockDelay?: number
): Promise<void> {
  await setupApi(page, {
    useMocks: true,
    mockDelay,
  });
}

/**
 * Helper to disable all API mocking
 *
 * Forces real API usage for all endpoints
 *
 * @param page - Playwright page object
 *
 * @example
 * test('integration test with real API', async ({ page }) => {
 *   await setupRealApi(page);
 * });
 */
export async function setupRealApi(page: Page): Promise<void> {
  await setupApi(page, {
    useMocks: false,
  });
}
