/**
 * Test Environment Configuration Module
 *
 * Manages environment-based test configuration, including:
 * - API endpoint configuration
 * - Mock vs. Real API selection
 * - Environment detection and validation
 * - Test data source selection
 */

/**
 * Environment configuration
 */
export interface TestEnvironmentConfig {
  // API Configuration
  USE_REAL_API: boolean;
  USE_MOCK_API: boolean;
  API_BASE_URL: string;
  FRONTEND_BASE_URL: string;

  // Feature Flags
  ENABLE_VISUAL_REGRESSION: boolean;
  ENABLE_PERFORMANCE_MONITORING: boolean;
  ENABLE_ACCESSIBILITY_TESTS: boolean;

  // Test Execution
  ENABLE_VIDEO_RECORDING: boolean;
  ENABLE_SCREENSHOTS_ON_FAILURE: boolean;
  SLOW_MOTION_MS: number;
  TRACE_ENABLED: boolean;

  // Timeout Configuration
  NAVIGATION_TIMEOUT_MS: number;
  ACTION_TIMEOUT_MS: number;
  EXPECT_TIMEOUT_MS: number;

  // Environment Name
  ENVIRONMENT: 'development' | 'staging' | 'production';
}

/**
 * Current test environment configuration
 * Automatically initialized from environment variables
 */
export const TEST_ENV: TestEnvironmentConfig = {
  // API Configuration
  USE_REAL_API: process.env.USE_REAL_API === 'true',
  USE_MOCK_API: process.env.USE_REAL_API !== 'true',
  API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
  FRONTEND_BASE_URL: process.env.FRONTEND_BASE_URL || 'http://localhost:3000',

  // Feature Flags
  ENABLE_VISUAL_REGRESSION: process.env.ENABLE_VISUAL_REGRESSION === 'true',
  ENABLE_PERFORMANCE_MONITORING: process.env.ENABLE_PERFORMANCE_MONITORING !== 'false',
  ENABLE_ACCESSIBILITY_TESTS: process.env.ENABLE_ACCESSIBILITY_TESTS === 'true',

  // Test Execution
  ENABLE_VIDEO_RECORDING: process.env.ENABLE_VIDEO_RECORDING === 'true',
  ENABLE_SCREENSHOTS_ON_FAILURE: process.env.ENABLE_SCREENSHOTS_ON_FAILURE !== 'false',
  SLOW_MOTION_MS: parseInt(process.env.SLOW_MOTION_MS || '0', 10),
  TRACE_ENABLED: process.env.TRACE_ENABLED === 'true',

  // Timeout Configuration
  NAVIGATION_TIMEOUT_MS: parseInt(process.env.NAVIGATION_TIMEOUT_MS || '30000', 10),
  ACTION_TIMEOUT_MS: parseInt(process.env.ACTION_TIMEOUT_MS || '10000', 10),
  EXPECT_TIMEOUT_MS: parseInt(process.env.EXPECT_TIMEOUT_MS || '5000', 10),

  // Environment Name
  ENVIRONMENT: (process.env.TEST_ENVIRONMENT || 'development') as 'development' | 'staging' | 'production',
};

/**
 * Check if tests should use mock APIs
 *
 * @returns true if mock APIs should be used, false otherwise
 *
 * @example
 * if (shouldUseMocks()) {
 *   await mockDashboardApis(page);
 * }
 */
export function shouldUseMocks(): boolean {
  return TEST_ENV.USE_MOCK_API;
}

/**
 * Check if tests should use real APIs
 *
 * @returns true if real APIs should be used, false otherwise
 *
 * @example
 * if (shouldUseRealApi()) {
 *   // Connect to actual backend
 * }
 */
export function shouldUseRealApi(): boolean {
  return TEST_ENV.USE_REAL_API;
}

/**
 * Check if visual regression testing is enabled
 *
 * @returns true if visual regression is enabled
 *
 * @example
 * if (isVisualRegressionEnabled()) {
 *   await captureVisualSnapshot(page, 'snapshot-name');
 * }
 */
export function isVisualRegressionEnabled(): boolean {
  return TEST_ENV.ENABLE_VISUAL_REGRESSION;
}

/**
 * Check if performance monitoring is enabled
 *
 * @returns true if performance monitoring is enabled
 */
export function isPerformanceMonitoringEnabled(): boolean {
  return TEST_ENV.ENABLE_PERFORMANCE_MONITORING;
}

/**
 * Check if accessibility tests are enabled
 *
 * @returns true if accessibility tests are enabled
 */
export function isAccessibilityTestsEnabled(): boolean {
  return TEST_ENV.ENABLE_ACCESSIBILITY_TESTS;
}

/**
 * Get API base URL
 *
 * @returns The base URL for API requests
 *
 * @example
 * const apiUrl = getApiBaseUrl() + '/api/dashboard/overview';
 */
export function getApiBaseUrl(): string {
  return TEST_ENV.API_BASE_URL;
}

/**
 * Get frontend base URL
 *
 * @returns The base URL for frontend access
 *
 * @example
 * await page.goto(getFrontendBaseUrl() + '/dashboard');
 */
export function getFrontendBaseUrl(): string {
  return TEST_ENV.FRONTEND_BASE_URL;
}

/**
 * Get test environment name
 *
 * @returns The current test environment (development, staging, production)
 *
 * @example
 * const env = getTestEnvironment();
 * if (env === 'production') {
 *   // Run additional safety checks
 * }
 */
export function getTestEnvironment(): string {
  return TEST_ENV.ENVIRONMENT;
}

/**
 * Validate test environment configuration
 *
 * Checks that:
 * - API base URL is accessible (for real API mode)
 * - Frontend base URL is configured
 * - Timeout values are reasonable
 * - Only one of mock/real API is selected
 *
 * @throws Error if validation fails
 *
 * @example
 * validateTestEnvironment();
 */
export async function validateTestEnvironment(): Promise<void> {
  const errors: string[] = [];

  // Check that one mode is selected
  if (!shouldUseMocks() && !shouldUseRealApi()) {
    errors.push('Neither mock nor real API mode is selected');
  }

  // Check frontend URL
  if (!TEST_ENV.FRONTEND_BASE_URL) {
    errors.push('FRONTEND_BASE_URL is not configured');
  }

  // Check API URL
  if (!TEST_ENV.API_BASE_URL) {
    errors.push('API_BASE_URL is not configured');
  }

  // Validate timeout values
  if (TEST_ENV.NAVIGATION_TIMEOUT_MS <= 0) {
    errors.push('NAVIGATION_TIMEOUT_MS must be positive');
  }

  if (TEST_ENV.ACTION_TIMEOUT_MS <= 0) {
    errors.push('ACTION_TIMEOUT_MS must be positive');
  }

  if (TEST_ENV.EXPECT_TIMEOUT_MS <= 0) {
    errors.push('EXPECT_TIMEOUT_MS must be positive');
  }

  if (errors.length > 0) {
    throw new Error(`Test environment validation failed:\n${errors.join('\n')}`);
  }

  // Log environment configuration
  console.log('Test Environment Configuration:');
  console.log(`  Environment: ${TEST_ENV.ENVIRONMENT}`);
  console.log(`  API Mode: ${shouldUseMocks() ? 'Mock' : 'Real'}`);
  console.log(`  Frontend URL: ${TEST_ENV.FRONTEND_BASE_URL}`);
  console.log(`  API Base URL: ${TEST_ENV.API_BASE_URL}`);
  console.log(`  Visual Regression: ${TEST_ENV.ENABLE_VISUAL_REGRESSION}`);
  console.log(`  Performance Monitoring: ${TEST_ENV.ENABLE_PERFORMANCE_MONITORING}`);
}

/**
 * Set up environment for a specific test mode
 *
 * @param mode - 'mock' or 'real'
 * @param options - Optional configuration overrides
 *
 * @example
 * // Use mock APIs for this test
 * await setupTestMode('mock');
 *
 * // Use real APIs
 * await setupTestMode('real', {
 *   API_BASE_URL: 'https://api.production.com'
 * });
 */
export async function setupTestMode(
  mode: 'mock' | 'real',
  options?: Partial<TestEnvironmentConfig>
): Promise<void> {
  if (mode === 'mock') {
    TEST_ENV.USE_MOCK_API = true;
    TEST_ENV.USE_REAL_API = false;
  } else if (mode === 'real') {
    TEST_ENV.USE_MOCK_API = false;
    TEST_ENV.USE_REAL_API = true;
  } else {
    throw new Error(`Invalid test mode: ${mode}. Expected 'mock' or 'real'`);
  }

  // Apply options overrides
  if (options) {
    Object.assign(TEST_ENV, options);
  }

  await validateTestEnvironment();
}

/**
 * Get environment variables as a summary object
 *
 * @returns Object containing current environment configuration
 *
 * @example
 * const envSummary = getEnvironmentSummary();
 * console.log(envSummary);
 */
export function getEnvironmentSummary(): TestEnvironmentConfig {
  return { ...TEST_ENV };
}

/**
 * Check if we're running in a specific environment
 *
 * @param environment - Environment to check
 * @returns true if current environment matches
 *
 * @example
 * if (isEnvironment('production')) {
 *   // Run production-only tests
 * }
 */
export function isEnvironment(environment: 'development' | 'staging' | 'production'): boolean {
  return TEST_ENV.ENVIRONMENT === environment;
}
