/**
 * Phase 4: Server-Sent Events (SSE) Testing Helpers
 *
 * Utilities for testing Server-Sent Events connections, real-time data streams,
 * and event-based communication in E2E tests.
 *
 * @module tests/helpers/sse-tester
 */

import { Page } from '@playwright/test';

/**
 * Create an SSE tester instance
 *
 * @param page - Playwright page object
 * @param options - Connection options
 * @returns New SSETester instance
 */
export function createSSETester(page: Page, options?: SSEOptions): SSETester {
  return new SSETester(page, options);
}

export default {
  SSETester,
  createSSETester,
};

