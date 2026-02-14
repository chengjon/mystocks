/**
 * API Helper Functions for E2E Testing
 *
 * Provides utilities for mocking APIs, intercepting requests,
 * and managing test data during E2E tests.
 *
 * Version: 1.0.0
 * Date: 2025-12-04
 */

import { Page, Route } from '@playwright/test';

/**
 * Mock trade management APIs
 */
export async function mockTradeManagementApis(page: Page): Promise<void> {
  const mocks: MockApiConfig[] = [
    {
      method: 'GET',
      urlPattern: '/api/trading/orders',
      response: {
        body: mockOrdersData,
      },
      delay: 300,
    },
    {
      method: 'GET',
      urlPattern: '/api/portfolio/positions',
      response: {
        body: mockPositionsData,
      },
      delay: 300,
    },
  ];

  await setupMockApis(page, mocks);
}

/**
 * Wait for specific API call
 */
export async function waitForApiCall(page: Page, urlPattern: string | RegExp, timeout: number = 10000): Promise<void> {
  const regex = typeof urlPattern === 'string' ? new RegExp(urlPattern) : urlPattern;

  return Promise.race([
    page.waitForResponse((response) => regex.test(response.url())),
    new Promise<void>((_, reject) =>
      setTimeout(() => reject(new Error(`API call timeout: ${urlPattern}`)), timeout)
    ),
  ]).then(() => {});
}

/**
 * Intercept and verify API call
 */
export async function interceptAndVerifyApi(
  page: Page,
  urlPattern: string | RegExp,
  verification: (body: Record<string, any>) => boolean,
  timeout: number = 10000
): Promise<boolean> {
  const regex = typeof urlPattern === 'string' ? new RegExp(urlPattern) : urlPattern;

  try {
    const response = await Promise.race([
      page.waitForResponse((response) => regex.test(response.url())),
      new Promise<any>((_, reject) =>
        setTimeout(() => reject(new Error(`Timeout waiting for ${urlPattern}`)), timeout)
      ),
    ]);

    if (response.ok()) {
      const body = await response.json();
      return verification(body);
    }

    return false;
  } catch {
    return false;
  }
}

/**
 * Simulate network error
 */
export async function simulateNetworkError(page: Page, urlPattern: string | RegExp): Promise<void> {
  const regex = typeof urlPattern === 'string' ? new RegExp(urlPattern) : urlPattern;

  await page.route(regex, (route) => {
    route.abort('failed');
  });
}

/**
 * Simulate slow network
 */
export async function simulateSlowNetwork(page: Page, delayMs: number): Promise<void> {
  await page.route('**/*', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    await route.continue();
  });
}

/**
 * Clear all route mocks
 */
export async function clearMocks(page: Page): Promise<void> {
  await page.unroute('**/*');
}

