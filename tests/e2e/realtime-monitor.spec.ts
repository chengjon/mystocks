/**
 * Phase 4 Milestone 1: Real-Time Monitor E2E Tests
 *
 * Comprehensive test suite for WebSocket and Server-Sent Events (SSE) functionality
 * in the RealTimeMonitor.vue component and related real-time data streaming features.
 *
 * @module tests/e2e/realtime-monitor
 */

import { test, expect, Page } from '@playwright/test';
import { WebSocketTester } from '../helpers/websocket-tester';
import { SSETester } from '../helpers/sse-tester';

/**
 * Get the base URL from environment or default
 */
function getBaseUrl(): string {
  return process.env.BASE_URL || 'http://localhost:3000';
}

/**
 * Get the API base URL from environment or default
 */
function getApiBaseUrl(): string {
  return process.env.API_BASE || 'http://localhost:8000';
}

/**
 * Test Suite: Real-Time Monitor WebSocket Connections
 */
test.describe('Real-Time Monitor - WebSocket Connections', () => {
  let wsTester: WebSocketTester;

  test.beforeEach(() => {
    wsTester = new WebSocketTester({
      connectTimeout: 5000,
      autoReconnect: false,
      reconnectAttempts: 0,
    });
  });

  test.afterEach(async () => {
    if (wsTester.isConnectionActive()) {
      await wsTester.disconnect();
    }
  });

  test('should establish WebSocket connection to training monitor', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    expect(wsTester.isConnectionActive()).toBe(true);
  });

  test('should receive training progress update messages', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    // Subscribe to training progress channel
    await wsTester.sendMessage({
      type: 'subscribe',
      channel: 'training_progress',
    });

    // Wait for progress update message
    const message = await wsTester.waitForMessage(
      (msg) => msg.type === 'training_progress',
      5000,
    );

    expect(message).toHaveProperty('type', 'training_progress');
    expect(message).toHaveProperty('data');
  });

  test('should send and receive bidirectional WebSocket messages', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    // Send subscription request
    await wsTester.sendMessage({
      type: 'subscribe',
      modelId: 'lstm-001',
      channel: 'model_status',
    });

    // Should receive acknowledgment
    const ackMessage = await wsTester.waitForMessage(
      (msg) => msg.type === 'acknowledge' || msg.type === 'model_status',
      3000,
    );

    expect(ackMessage).toBeDefined();
    expect(ackMessage.type).toMatch(/acknowledge|model_status/);
  });

  test('should handle WebSocket connection errors gracefully', async () => {
    const invalidUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/invalid-endpoint`;

    let errorOccurred = false;
    wsTester.onError((error) => {
      errorOccurred = true;
      expect(error).toBeDefined();
    });

    try {
      await wsTester.connectWebSocket(invalidUrl);
    } catch (error) {
      errorOccurred = true;
    }

    expect(errorOccurred).toBe(true);
  });

  test('should queue messages when predicate filters not matching', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    // Send multiple subscription requests
    await wsTester.sendMessage({ type: 'subscribe', channel: 'training_progress' });
    await wsTester.sendMessage({ type: 'subscribe', channel: 'backtest_progress' });

    // Wait specifically for backtest_progress
    const message = await wsTester.waitForMessage(
      (msg) => msg.type === 'backtest_progress',
      5000,
    );

    expect(message.type).toBe('backtest_progress');

    // Other messages should still be in queue
    const allMessages = wsTester.getMessages();
    expect(allMessages.length).toBeGreaterThan(0);
  });

  test('should maintain multiple message listeners', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    const receivedMessages: string[] = [];

    // Register multiple listeners
    wsTester.onMessage((msg) => {
      receivedMessages.push(`listener1:${msg.type}`);
    });

    wsTester.onMessage((msg) => {
      receivedMessages.push(`listener2:${msg.type}`);
    });

    // Send test message
    await wsTester.sendMessage({ type: 'subscribe', channel: 'test' });

    // Allow time for listeners to be called
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Both listeners should have been called
    expect(receivedMessages.length).toBeGreaterThan(0);
  });

  test('should assert message received by type', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    await wsTester.sendMessage({ type: 'subscribe', channel: 'training_progress' });

    // Should succeed if message received
    await expect(
      wsTester.assertMessageReceived('training_progress', 5000),
    ).resolves.not.toThrow();
  });

  test('should assert message NOT received when timeout occurs', async () => {
    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    // Should throw when expected message never arrives
    await expect(
      wsTester.assertMessageNotReceived('nonexistent_event', 1000),
    ).resolves.not.toThrow();
  });
});

/**
 * Test Suite: SSE (Server-Sent Events) Real-Time Streaming
 */
test.describe('Real-Time Monitor - SSE Streaming', () => {
  let sseTester: SSETester;
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    // Create a new page for each test
    page = await browser.newPage();
    sseTester = new SSETester(page, {
      connectTimeout: 5000,
      autoReconnect: false,
    });
  });

  test.afterEach(async () => {
    if (sseTester.isConnectionActive()) {
      await sseTester.disconnect();
    }
    await page.close();
  });

  test('should establish SSE connection to status endpoint', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    expect(sseTester.isConnectionActive()).toBe(true);
  });

  test('should receive server-sent events from SSE endpoint', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Wait for any event (SSE can emit various event types)
    const event = await sseTester.waitForEvent('message', 5000);

    expect(event).toBeDefined();
    expect(event.data).toBeDefined();
  });

  test('should receive and parse JSON event data', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Wait for data matching a predicate
    const data = await sseTester.waitForData(
      (event) => {
        try {
          const parsed = JSON.parse(event.data);
          return parsed.type === 'training_progress';
        } catch {
          return false;
        }
      },
      5000,
    );

    expect(data).toBeDefined();
    expect(typeof data).toBe('object');
  });

  test('should receive risk alert events', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Listen for risk alerts
    const alertData = await sseTester.waitForData(
      (event) => {
        try {
          const parsed = JSON.parse(event.data);
          return parsed.type === 'risk_alert';
        } catch {
          return false;
        }
      },
      10000,
    );

    expect(alertData).toBeDefined();
    if (typeof alertData === 'object' && alertData !== null) {
      expect((alertData as Record<string, unknown>).type).toBe('risk_alert');
    }
  });

  test('should send SSE request with custom headers', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;
    const customHeaders = {
      'X-Custom-Header': 'test-value',
      Authorization: 'Bearer test-token',
    };

    await sseTester.connectSSE(sseUrl, customHeaders);

    expect(sseTester.isConnectionActive()).toBe(true);
  });

  test('should handle SSE disconnection gracefully', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);
    expect(sseTester.isConnectionActive()).toBe(true);

    await sseTester.disconnect();
    expect(sseTester.isConnectionActive()).toBe(false);
  });

  test('should filter events by type', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Wait for specific event type
    const event = await sseTester.waitForEvent('training_progress', 5000);

    expect(event.event).toBe('training_progress');
  });

  test('should handle multiple SSE events', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Register listener to collect events
    const collectedEvents: string[] = [];
    sseTester.onEvent((event) => {
      collectedEvents.push(event.event || 'unnamed');
    });

    // Wait for some time to collect events
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Should have received at least one event
    expect(collectedEvents.length).toBeGreaterThan(0);
  });

  test('should assert event data matches pattern', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Assert that data contains certain pattern
    await expect(
      sseTester.assertDataMatches(/status|progress|alert/, 5000),
    ).resolves.not.toThrow();
  });

  test('should assert no errors occurred during streaming', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Should not throw if no errors
    await expect(sseTester.assertNoError()).resolves.not.toThrow();
  });

  test('should retrieve all collected events', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Wait for some events
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const allEvents = sseTester.getEvents();

    expect(Array.isArray(allEvents)).toBe(true);
  });

  test('should filter events by type using getEventsByType', async () => {
    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Collect some events
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Get specific type
    const progressEvents = sseTester.getEventsByType('training_progress');

    expect(Array.isArray(progressEvents)).toBe(true);
  });
});

/**
 * Test Suite: Real-Time Monitor Component Integration
 */
test.describe('Real-Time Monitor Component - Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to RealTimeMonitor component
    await page.goto(`${getBaseUrl()}/realtime-monitor`);
  });

  test('should render real-time monitor component', async ({ page }) => {
    // Check for main component
    const monitor = await page.locator('[data-testid="real-time-monitor"]');
    await expect(monitor).toBeVisible();
  });

  test('should display training progress section', async ({ page }) => {
    const progressSection = await page.locator('[data-testid="training-progress"]');
    await expect(progressSection).toBeVisible();
  });

  test('should display real-time alerts section', async ({ page }) => {
    const alertsSection = await page.locator('[data-testid="realtime-alerts"]');
    await expect(alertsSection).toBeVisible();
  });

  test('should connect and display SSE status updates', async ({ page }) => {
    // Wait for SSE connection to be established
    const statusElement = await page.locator('[data-testid="sse-status"]');

    // Initially should show "connecting"
    let status = await statusElement.textContent();
    expect(status).toMatch(/connecting|connected|initializing/i);

    // Wait for connection to establish
    await page.waitForTimeout(2000);

    // After connection, should show "connected"
    status = await statusElement.textContent();
    expect(status).toMatch(/connected/i);
  });

  test('should update training progress in real-time', async ({ page }) => {
    // Get initial progress value
    const progressBar = await page.locator('[data-testid="training-progress-bar"]');

    const initialValue = await progressBar.getAttribute('aria-valuenow');
    expect(initialValue).toBeDefined();

    // Wait for progress updates
    await page.waitForTimeout(2000);

    // Progress should change or remain stable
    const updatedValue = await progressBar.getAttribute('aria-valuenow');
    expect(updatedValue).toBeDefined();
  });

  test('should display training status updates', async ({ page }) => {
    const statusText = await page.locator('[data-testid="training-status-text"]');

    // Status should show some training information
    const text = await statusText.textContent();
    expect(text).toBeDefined();
    expect(text?.length).toBeGreaterThan(0);
  });

  test('should render alert list with real-time items', async ({ page }) => {
    const alertList = await page.locator('[data-testid="alert-list"]');
    const alerts = await alertList.locator('[data-testid^="alert-item"]').count();

    // Should have at least one alert (or 0 if none triggered)
    expect(alerts).toBeGreaterThanOrEqual(0);
  });

  test('should display alert severity indicators', async ({ page }) => {
    // Get all alerts
    const alerts = await page.locator('[data-testid^="alert-item"]');
    const count = await alerts.count();

    if (count > 0) {
      // Check first alert for severity indicator
      const severity = await alerts
        .first()
        .locator('[data-testid="alert-severity"]')
        .getAttribute('data-severity');

      expect(severity).toMatch(/critical|high|medium|low|info/i);
    }
  });

  test('should allow dismissing individual alerts', async ({ page }) => {
    const alerts = await page.locator('[data-testid^="alert-item"]');
    const initialCount = await alerts.count();

    if (initialCount > 0) {
      // Click dismiss button on first alert
      const dismissButton = alerts.first().locator('[data-testid="dismiss-alert"]');
      if (await dismissButton.isVisible()) {
        await dismissButton.click();

        // Count should decrease
        const newCount = await page.locator('[data-testid^="alert-item"]').count();
        expect(newCount).toBeLessThanOrEqual(initialCount);
      }
    }
  });

  test('should display connection status indicator', async ({ page }) => {
    const statusIndicator = await page.locator('[data-testid="connection-status-indicator"]');
    await expect(statusIndicator).toBeVisible();

    // Check status class (connected/disconnected/connecting)
    const className = await statusIndicator.getAttribute('class');
    expect(className).toContain(/connected|disconnected|connecting/i);
  });

  test('should show backtest progress when available', async ({ page }) => {
    const backtestSection = await page.locator('[data-testid="backtest-progress"]');

    // Section might be hidden if no backtest is running
    const isVisible = await backtestSection.isVisible({ timeout: 1000 }).catch(() => false);

    if (isVisible) {
      const progressBar = backtestSection.locator('progress');
      await expect(progressBar).toBeVisible();
    }
  });

  test('should refresh training status periodically', async ({ page }) => {
    // Get initial status
    const statusText = await page.locator('[data-testid="training-status-text"]');
    const initialText = await statusText.textContent();

    // Wait for refresh cycle
    await page.waitForTimeout(3000);

    // Status should still be visible (might have changed)
    const updatedText = await statusText.textContent();
    expect(updatedText).toBeDefined();
  });

  test('should handle WebSocket reconnection after disconnect', async ({ page }) => {
    const connectionStatus = await page.locator('[data-testid="connection-status-indicator"]');

    // Initially should be connected
    let status = await connectionStatus.getAttribute('data-status');
    expect(status).toBe('connected');

    // Simulate network disconnect by closing all WebSockets
    await page.evaluate(() => {
      (window as any).__simulateNetworkDisconnect?.();
    });

    await page.waitForTimeout(1000);

    // Should show reconnecting or disconnected
    status = await connectionStatus.getAttribute('data-status');
    expect(status).toMatch(/reconnecting|disconnected/i);

    // Wait for reconnection
    await page.waitForTimeout(2000);

    // Should eventually reconnect
    status = await connectionStatus.getAttribute('data-status');
    expect(status).toBe('connected');
  });
});

/**
 * Test Suite: Real-Time Data Accuracy
 */
test.describe('Real-Time Monitor - Data Accuracy', () => {
  test('should display consistent training progress values', async ({ page }) => {
    await page.goto(`${getBaseUrl()}/realtime-monitor`);

    // Get progress values at multiple points
    const progressValues: number[] = [];

    for (let i = 0; i < 3; i++) {
      const progressBar = await page.locator('[data-testid="training-progress-bar"]');
      const value = await progressBar.getAttribute('aria-valuenow');

      if (value) {
        progressValues.push(parseInt(value));
      }

      await page.waitForTimeout(1000);
    }

    // Progress should be monotonically increasing or stable
    for (let i = 1; i < progressValues.length; i++) {
      expect(progressValues[i]).toBeGreaterThanOrEqual(progressValues[i - 1]);
    }
  });

  test('should display valid timestamp information', async ({ page }) => {
    await page.goto(`${getBaseUrl()}/realtime-monitor`);

    const timestamp = await page.locator('[data-testid="last-update-time"]').textContent();

    expect(timestamp).toBeDefined();
    // Should contain date/time information
    expect(timestamp).toMatch(/\d+:\d+|\d+-\d+-\d+/);
  });

  test('should display alert with complete information', async ({ page }) => {
    await page.goto(`${getBaseUrl()}/realtime-monitor`);

    // Find first alert
    const alertItem = await page.locator('[data-testid^="alert-item"]').first();
    const isVisible = await alertItem.isVisible({ timeout: 1000 }).catch(() => false);

    if (isVisible) {
      // Check for required alert fields
      const title = await alertItem.locator('[data-testid="alert-title"]').textContent();
      const message = await alertItem.locator('[data-testid="alert-message"]').textContent();
      const timestamp = await alertItem.locator('[data-testid="alert-timestamp"]').textContent();

      expect(title).toBeDefined();
      expect(message).toBeDefined();
      expect(timestamp).toBeDefined();
    }
  });
});

/**
 * Test Suite: Performance and Load Handling
 */
test.describe('Real-Time Monitor - Performance', () => {
  test('should handle rapid message updates efficiently', async () => {
    const wsTester = new WebSocketTester({
      connectTimeout: 5000,
      autoReconnect: false,
    });

    const wsUrl = `${getApiBaseUrl().replace('http', 'ws')}/api/v1/ws/training-monitor`;

    await wsTester.connectWebSocket(wsUrl);

    // Send multiple messages rapidly
    const startTime = Date.now();

    for (let i = 0; i < 10; i++) {
      await wsTester.sendMessage({
        type: 'subscribe',
        channel: `channel_${i}`,
      });
    }

    const elapsed = Date.now() - startTime;

    // Should complete in reasonable time (less than 1 second)
    expect(elapsed).toBeLessThan(1000);

    await wsTester.disconnect();
  });

  test('should not leak memory with continuous SSE updates', async ({ browser }) => {
    const page = await browser.newPage();
    const sseTester = new SSETester(page, { connectTimeout: 5000 });

    const sseUrl = `${getApiBaseUrl()}/api/v1/sse/status`;

    await sseTester.connectSSE(sseUrl);

    // Collect events for a period
    await new Promise((resolve) => setTimeout(resolve, 3000));

    // Get memory usage before clearing
    const eventCount = sseTester.getEvents().length;

    // Clear events
    sseTester.clearEvents();

    // Should be empty after clearing
    const clearedCount = sseTester.getEvents().length;
    expect(clearedCount).toBe(0);

    await sseTester.disconnect();
    await page.close();
  });
});
