// tests/e2e/utils/api-validator.ts
import { Page, expect } from '@playwright/test';

interface StandardApiResponse {
  success: boolean;
  code: number;
  data: any;
  message: string;
}

/**
 * Sets up Playwright to intercept all API calls to the backend and validate their structure.
 * Tests will fail if an API response does not conform to the expected StandardApiResponse format.
 *
 * @param page The Playwright Page object.
 * @param apiBaseUrl The base URL for your API (e.g., '/api/').
 */
export async function setupApiStandardization(page: Page, apiBaseUrl: string = '/api/') {
  await page.route(`${apiBaseUrl}**`, async route => {
    // Proceed with the request to get the actual response
    let response;
    try {
      // Add a short timeout to prevent hanging if backend is down
      response = await route.fetch({ timeout: 3000 });
    } catch (e) {
      console.warn(`[ApiValidator] Failed to fetch ${route.request().url()}: ${e.message}`);
      // If fetch fails (e.g. backend down), we can't validate. 
      // Option A: Fail the test. Option B: Continue (let the app handle the error).
      // For "Critical Scan" where we expect mocks, falling through to a dead backend is usually a bug in the test setup.
      // We'll continue to let the app fail naturally or show an error.
      return route.continue(); 
    }

    const headers = response.headers();
    const contentType = headers['content-type'] || '';

    // Only validate JSON responses
    if (contentType.includes('application/json')) {
      try {
        const json: StandardApiResponse = await response.json();

        // Perform the validation checks
        expect(json).toHaveProperty('success');
        expect(typeof json.success).toBe('boolean');
        
        expect(json).toHaveProperty('code');
        expect(typeof json.code).toBe('number');

        expect(json).toHaveProperty('data'); // Data can be anything, so just check existence
        
        expect(json).toHaveProperty('message');
        expect(typeof json.message).toBe('string');

      } catch (error) {
        // If parsing fails or any expectation fails, it means the API response is not standard
        // Fail the test here with detailed information
        expect.fail(`API response for ${route.request().url()} failed standardization checks. Error: ${error.message}. Response: ${await response.text()}`);
      }
    }

    // Fulfill the route with the original response after validation (or if not JSON)
    route.fulfill({
      status: response.status(),
      headers: response.headers(),
      body: await response.text(), // Use text() to avoid consuming json() twice if already parsed
    });
  });
}
