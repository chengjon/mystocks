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
 * Mock API response configuration
 */
export interface MockApiConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  urlPattern: string | RegExp;
  response: {
    status?: number;
    contentType?: string;
    body: Record<string, any> | string;
  };
  delay?: number; // Simulate network delay in ms
}

/**
 * Mock data for dashboard
 */
export const mockDashboardData = {
  overview: {
    success: true,
    data: {
      total_asset: 1000000,
      daily_return: 2500,
      daily_return_percentage: 2.5,
      position_count: 5,
      order_count: 2,
      alert_count: 1,
    },
    timestamp: new Date().toISOString(),
  },
};

/**
 * Mock data for market
 */
export const mockMarketData = {
  stocks: [
    {
      symbol: '000001',
      name: '平安银行',
      price: 10.5,
      change: 2.5,
      change_percent: 2.43,
      volume: 100000000,
      market_cap: 1000000000000,
    },
    {
      symbol: '600000',
      name: '浦发银行',
      price: 8.2,
      change: -0.1,
      change_percent: -1.2,
      volume: 50000000,
      market_cap: 500000000000,
    },
    {
      symbol: '601988',
      name: '中国银行',
      price: 3.5,
      change: 0.05,
      change_percent: 1.45,
      volume: 200000000,
      market_cap: 700000000000,
    },
  ],
  total: 3,
  page: 1,
  page_size: 20,
};

/**
 * Mock data for stock detail
 */
export const mockStockDetailData = {
  symbol: '000001',
  name: '平安银行',
  price: 10.5,
  change: 0.25,
  change_percent: 2.43,
  high: 10.6,
  low: 10.2,
  open: 10.25,
  close: 10.5,
  volume: 100000000,
  market_cap: 1000000000000,
  pe_ratio: 8.5,
  pb_ratio: 0.9,
  dividend_yield: 3.2,
};

/**
 * Mock data for technical indicators
 */
export const mockIndicatorRegistry = {
  total: 161,
  categories: [
    { name: 'Overlap Studies', count: 22 },
    { name: 'Momentum Indicators', count: 25 },
    { name: 'Volume Indicators', count: 7 },
    { name: 'Volatility Indicators', count: 10 },
    { name: 'Price Transform', count: 5 },
    { name: 'Cycle Indicators', count: 5 },
    { name: 'Pattern Recognition', count: 10 },
    { name: 'Statistic Functions', 10 },
  ],
  indicators: [
    {
      name: 'Simple Moving Average',
      abbr: 'SMA',
      category: 'Overlap Studies',
      description: 'Simple moving average',
      parameters: [
        { name: 'period', type: 'int', default: 20, min: 1, max: 500 },
      ],
    },
    {
      name: 'Relative Strength Index',
      abbr: 'RSI',
      category: 'Momentum Indicators',
      description: 'Relative strength index',
      parameters: [
        { name: 'period', type: 'int', default: 14, min: 1, max: 100 },
      ],
    },
    {
      name: 'Moving Average Convergence Divergence',
      abbr: 'MACD',
      category: 'Momentum Indicators',
      description: 'MACD indicator',
      parameters: [
        { name: 'fast_period', type: 'int', default: 12, min: 1, max: 100 },
        { name: 'slow_period', type: 'int', default: 26, min: 1, max: 100 },
        { name: 'signal_period', type: 'int', default: 9, min: 1, max: 50 },
      ],
    },
  ],
};

/**
 * Mock data for trading orders
 */
export const mockOrdersData = {
  orders: [
    {
      id: 'ORD001',
      symbol: '000001',
      side: 'BUY',
      quantity: 100,
      price: 10.5,
      status: 'FILLED',
      filled_quantity: 100,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      filled_at: new Date(Date.now() - 3000000).toISOString(),
    },
    {
      id: 'ORD002',
      symbol: '600000',
      side: 'SELL',
      quantity: 50,
      price: 8.2,
      status: 'PENDING',
      filled_quantity: 0,
      created_at: new Date(Date.now() - 1800000).toISOString(),
    },
  ],
  total: 2,
};

/**
 * Mock data for positions
 */
export const mockPositionsData = {
  positions: [
    {
      id: 'POS001',
      symbol: '000001',
      name: '平安银行',
      quantity: 100,
      cost_price: 10.25,
      current_price: 10.5,
      market_value: 1050,
      cost: 1025,
      profit_loss: 25,
      profit_loss_percent: 2.43,
      opened_at: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: 'POS002',
      symbol: '600000',
      name: '浦发银行',
      quantity: 50,
      cost_price: 8.3,
      current_price: 8.2,
      market_value: 410,
      cost: 415,
      profit_loss: -5,
      profit_loss_percent: -1.2,
      opened_at: new Date(Date.now() - 172800000).toISOString(),
    },
  ],
  total: 2,
};

/**
 * Setup mock API responses for a page
 */
export async function setupMockApis(page: Page, mocks: MockApiConfig[]): Promise<void> {
  await page.route('**/*', async (route: Route) => {
    const request = route.request();
    const url = request.url();
    const method = request.method();

    // Find matching mock configuration
    const matchingMock = mocks.find((mock) => {
      const urlMatches = typeof mock.urlPattern === 'string' ? url.includes(mock.urlPattern) : mock.urlPattern.test(url);
      const methodMatches = !mock.method || mock.method === method;
      return urlMatches && methodMatches;
    });

    if (matchingMock) {
      // Simulate network delay if specified
      if (matchingMock.delay) {
        await new Promise((resolve) => setTimeout(resolve, matchingMock.delay!));
      }

      // Return mocked response
      await route.abort('blockedbyclient'); // Stop actual request
      const body =
        typeof matchingMock.response.body === 'string'
          ? matchingMock.response.body
          : JSON.stringify(matchingMock.response.body);

      await route.respond({
        status: matchingMock.response.status || 200,
        contentType: matchingMock.response.contentType || 'application/json',
        body,
      });
    } else {
      // Allow real request
      await route.continue();
    }
  });
}

/**
 * Mock dashboard APIs
 */
export async function mockDashboardApis(page: Page): Promise<void> {
  const mocks: MockApiConfig[] = [
    {
      method: 'GET',
      urlPattern: '/api/dashboard/overview',
      response: {
        body: mockDashboardData,
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
 * Mock market APIs
 */
export async function mockMarketApis(page: Page): Promise<void> {
  const mocks: MockApiConfig[] = [
    {
      method: 'GET',
      urlPattern: /\/api\/market\/(overview|data|search)/,
      response: {
        body: { ...mockMarketData, timestamp: new Date().toISOString() },
      },
      delay: 500,
    },
  ];

  await setupMockApis(page, mocks);
}

/**
 * Mock stock detail APIs
 */
export async function mockStockDetailApis(page: Page, symbol: string = '000001'): Promise<void> {
  const mocks: MockApiConfig[] = [
    {
      method: 'GET',
      urlPattern: new RegExp(`/api/market/stock/${symbol}/detail`),
      response: {
        body: { ...mockStockDetailData, timestamp: new Date().toISOString() },
      },
      delay: 400,
    },
    {
      method: 'GET',
      urlPattern: /\/api\/technical\/chart/,
      response: {
        body: {
          data: Array.from({ length: 100 }, (_, i) => ({
            timestamp: new Date(Date.now() - (100 - i) * 86400000).toISOString(),
            open: 10 + Math.random(),
            high: 10.5 + Math.random(),
            low: 9.5 + Math.random(),
            close: 10 + Math.random(),
            volume: Math.floor(Math.random() * 100000000),
          })),
        },
      },
      delay: 600,
    },
  ];

  await setupMockApis(page, mocks);
}

/**
 * Mock technical analysis APIs
 */
export async function mockTechnicalAnalysisApis(page: Page): Promise<void> {
  const mocks: MockApiConfig[] = [
    {
      method: 'GET',
      urlPattern: '/api/technical/indicators/registry',
      response: {
        body: mockIndicatorRegistry,
      },
      delay: 400,
    },
    {
      method: 'POST',
      urlPattern: '/api/technical/calculate',
      response: {
        body: { data: [], success: true },
      },
      delay: 800,
    },
  ];

  await setupMockApis(page, mocks);
}

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
