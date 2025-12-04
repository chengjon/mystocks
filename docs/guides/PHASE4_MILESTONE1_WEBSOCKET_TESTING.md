# Phase 4 Milestone 1: WebSocket & SSE Real-Time Testing Guide

**Status**: 🔄 In Progress
**Date**: 2025-12-05
**Milestone**: 1 of 4 (Advanced Testing Features)
**Duration**: 4-5 days

---

## Overview

This guide provides comprehensive documentation for testing real-time communication features in E2E tests, specifically WebSocket connections and Server-Sent Events (SSE) for streaming server-to-client updates.

### What You'll Learn

- How to test WebSocket connections and bidirectional messaging
- How to test Server-Sent Events (SSE) for unidirectional streaming
- Implementing timeout handling and error recovery
- Creating realistic real-time test scenarios
- Best practices for real-time feature testing

### Key Features

- ✅ **WebSocket Testing**: Full lifecycle management, message sending/receiving, event listening
- ✅ **SSE Testing**: EventSource connections, event filtering, JSON parsing
- ✅ **Error Handling**: Timeout management, connection errors, reconnection support
- ✅ **Message Filtering**: Predicate-based message filtering and validation
- ✅ **Event Listeners**: Register multiple listeners for different event types

---

## Part 1: WebSocket Testing

### 1.1 WebSocket Tester Overview

The `WebSocketTester` class provides utilities for testing WebSocket connections in Playwright E2E tests.

**File Location**: `tests/helpers/websocket-tester.ts`

**Key Capabilities**:
- Connection establishment with timeout handling
- Bidirectional message sending and receiving
- Event listener management
- Message queue for pending assertions
- Auto-reconnection support
- Connection state management

### 1.2 WebSocket Connection Lifecycle

#### Establishing a Connection

```typescript
import { WebSocketTester } from '../../tests/helpers/websocket-tester';

// Create tester instance with custom options
const wsTester = new WebSocketTester({
  connectTimeout: 5000,        // Maximum time to wait for connection
  autoReconnect: false,         // Don't auto-reconnect on disconnect
  reconnectAttempts: 3,         // Max reconnection attempts
  reconnectDelay: 1000,         // Delay between reconnection attempts
});

// Connect to WebSocket server
await wsTester.connectWebSocket('ws://localhost:8000/api/v1/ws/training-monitor');

// Connection established successfully
expect(wsTester.isConnectionActive()).toBe(true);
```

#### Sending Messages

```typescript
// Send a simple message
await wsTester.sendMessage({
  type: 'subscribe',
  channel: 'training_progress',
});

// Send with additional data
await wsTester.sendMessage({
  type: 'subscribe',
  modelId: 'lstm-001',
  channel: 'model_metrics',
  filters: {
    minAccuracy: 0.95,
  },
});

// Send string message
await wsTester.sendMessage('{"type": "ping"}');
```

#### Receiving Messages

```typescript
// Wait for any message
const message = await wsTester.waitForMessage(undefined, 5000);
console.log('Received:', message);

// Wait for specific message type
const progressMsg = await wsTester.waitForMessage(
  (msg) => msg.type === 'training_progress',
  5000,
);

// Wait for multiple messages
const updates = await wsTester.waitForMessages(5, 10000);
console.log(`Received ${updates.length} messages`);

// Wait for message matching complex predicate
const criticalAlert = await wsTester.waitForMessage(
  (msg) => msg.type === 'alert' && msg.severity === 'critical',
  5000,
);
```

#### Disconnecting

```typescript
// Clean disconnect
await wsTester.disconnect();

// Connection should be inactive
expect(wsTester.isConnectionActive()).toBe(false);
```

### 1.3 Event Listener Patterns

#### Single Listener

```typescript
// Register a listener for all messages
wsTester.onMessage((message) => {
  console.log('Message received:', message);
});

// Register error listener
wsTester.onError((error) => {
  console.error('WebSocket error:', error.message);
});

// Register close listener
wsTester.onClose(() => {
  console.log('WebSocket connection closed');
});
```

#### Multiple Listeners

```typescript
// You can register multiple listeners for different purposes
wsTester.onMessage((message) => {
  // Listener 1: Log all messages
  console.log('[DEBUG]', message);
});

wsTester.onMessage((message) => {
  // Listener 2: Validate message format
  if (!message.type) {
    console.warn('Invalid message format');
  }
});

wsTester.onMessage((message) => {
  // Listener 3: Update UI state
  updateMockUIState(message);
});
```

### 1.4 WebSocket Assertions

#### Assert Message Received

```typescript
// Assert that a specific message type was received
await wsTester.assertMessageReceived('training_progress', 5000);

// If message not received, assertion throws
// Error: Expected message of type 'training_progress' was not received
```

#### Assert Message NOT Received

```typescript
// Assert that an error message was NOT received
await wsTester.assertMessageNotReceived('error', 2000);

// This passes if the 'error' message is not received within 2 seconds
```

#### Assert Connection Closed

```typescript
// Assert that connection closes within timeout
await wsTester.assertConnectionClosed(5000);

// If connection doesn't close, throws error
// Error: Connection did not close within 5000ms
```

#### Assert Connected

```typescript
// Assert that connection is currently open
wsTester.assertConnected();

// If not connected, throws immediately
// Error: WebSocket is not connected
```

### 1.5 Message Queue Management

```typescript
// Get all messages received since connection
const allMessages = wsTester.getMessages();
console.log(`Received ${allMessages.length} messages total`);

// Messages are in receive order
allMessages.forEach((msg, index) => {
  console.log(`Message ${index + 1}:`, msg.type);
});

// Clear the message queue
wsTester.clearMessages();

// Queue is now empty
expect(wsTester.getMessages().length).toBe(0);
```

### 1.6 Real-World Example: Training Monitor

```typescript
import { test, expect } from '@playwright/test';
import { WebSocketTester } from '../helpers/websocket-tester';

test('monitor training progress over WebSocket', async () => {
  const wsTester = new WebSocketTester({
    connectTimeout: 5000,
    autoReconnect: true,
    reconnectAttempts: 3,
  });

  try {
    // Connect to training monitor
    await wsTester.connectWebSocket('ws://localhost:8000/api/v1/ws/training-monitor');
    console.log('Connected to training monitor');

    // Register listeners to track progress
    let progressUpdates = 0;
    wsTester.onMessage((msg) => {
      if (msg.type === 'training_progress') {
        progressUpdates++;
        console.log(`Progress update #${progressUpdates}:`, msg.data);
      }
    });

    // Subscribe to progress channel
    await wsTester.sendMessage({
      type: 'subscribe',
      channel: 'training_progress',
    });
    console.log('Subscribed to training_progress channel');

    // Wait for first progress update
    const firstProgress = await wsTester.waitForMessage(
      (msg) => msg.type === 'training_progress' && msg.data.progress > 0,
      5000,
    );
    console.log('First progress received:', firstProgress.data);

    // Verify progress is valid
    expect(firstProgress.data).toHaveProperty('progress');
    expect(firstProgress.data).toHaveProperty('modelId');
    expect(firstProgress.data).toHaveProperty('epoch');

    // Monitor multiple progress updates
    const updates = [];
    for (let i = 0; i < 3; i++) {
      const update = await wsTester.waitForMessage(
        (msg) => msg.type === 'training_progress',
        5000,
      );
      updates.push(update);
      console.log(`Update ${i + 1} - Progress: ${update.data.progress}%`);
    }

    // Verify progress is monotonically increasing
    for (let i = 1; i < updates.length; i++) {
      expect(updates[i].data.progress).toBeGreaterThanOrEqual(
        updates[i - 1].data.progress,
      );
    }

    console.log('Training progress monitoring test passed');
  } finally {
    await wsTester.disconnect();
  }
});
```

---

## Part 2: Server-Sent Events (SSE) Testing

### 2.1 SSE Tester Overview

The `SSETester` class provides utilities for testing Server-Sent Events connections in Playwright E2E tests.

**File Location**: `tests/helpers/sse-tester.ts`

**Key Capabilities**:
- EventSource connection management
- Event type filtering and listening
- JSON data parsing
- Custom header support
- Automatic reconnection handling
- Event query utilities

### 2.2 SSE Connection Lifecycle

#### Establishing a Connection

```typescript
import { SSETester } from '../../tests/helpers/sse-tester';

// Create tester instance with custom options
const sseTester = new SSETester(page, {
  connectTimeout: 5000,      // Maximum time to wait for connection
  autoReconnect: false,       // Don't auto-reconnect
  reconnectAttempts: 5,       // Max reconnection attempts
  reconnectDelay: 1000,       // Delay between attempts
});

// Connect to SSE endpoint
await sseTester.connectSSE('http://localhost:8000/api/v1/sse/status');

// Connection established
expect(sseTester.isConnectionActive()).toBe(true);
```

#### Connecting with Custom Headers

```typescript
// Send custom headers with the SSE request
const headers = {
  'X-User-ID': '12345',
  'X-Session-Token': 'abc123def456',
  'Authorization': 'Bearer token',
};

await sseTester.connectSSE('http://localhost:8000/api/v1/sse/status', headers);
```

#### Receiving Events

```typescript
// Wait for any event
const event = await sseTester.waitForEvent('message', 5000);
console.log('Event:', event.event, event.data);

// Wait for specific event type
const trainingEvent = await sseTester.waitForEvent('training_progress', 5000);
console.log('Training event:', trainingEvent.data);

// Wait for data matching predicate
const riskAlert = await sseTester.waitForData(
  (event) => {
    try {
      const data = JSON.parse(event.data);
      return data.type === 'risk_alert' && data.level === 'critical';
    } catch {
      return false;
    }
  },
  5000,
);
```

#### Disconnecting

```typescript
// Close the SSE connection
await sseTester.disconnect();

// Connection should be inactive
expect(sseTester.isConnectionActive()).toBe(false);
```

### 2.3 Event Listener Patterns

#### Event Listeners

```typescript
// Listen to all events
sseTester.onEvent((event) => {
  console.log(`Received event: ${event.event}`);
  console.log(`Data:`, event.data);
  if (event.parsedData) {
    console.log(`Parsed:`, event.parsedData);
  }
});

// Listen for errors
sseTester.onError((error) => {
  console.error('SSE error:', error.message);
});

// Listen for connection close
sseTester.onClose(() => {
  console.log('SSE connection closed');
});
```

### 2.4 SSE Assertions

#### Assert Event Received

```typescript
// Assert that an event type was received
await sseTester.assertEventReceived('training_progress', 5000);

// If event not received within timeout, throws error
// Error: Expected event 'training_progress' was not received
```

#### Assert Data Matches Pattern

```typescript
// Assert data matches regex pattern
await sseTester.assertDataMatches(/training|progress/, 5000);

// Assert data matches object pattern (checks specific properties)
await sseTester.assertDataMatches(
  {
    type: 'training_progress',
    status: 'running',
  },
  5000,
);
```

#### Assert No Errors

```typescript
// Assert that no errors occurred during streaming
await sseTester.assertNoError();

// If error listener is called, throws error
// Error: SSE error detected: [error message]
```

### 2.5 Event Query and Management

```typescript
// Get all events received
const allEvents = sseTester.getEvents();
console.log(`Total events received: ${allEvents.length}`);

// Get events of specific type
const trainingEvents = sseTester.getEventsByType('training_progress');
console.log(`Training progress events: ${trainingEvents.length}`);

// Examine event details
trainingEvents.forEach((event) => {
  console.log('Event:', {
    type: event.event,
    id: event.id,
    data: event.data,
    parsed: event.parsedData,
  });
});

// Clear event queue
sseTester.clearEvents();
expect(sseTester.getEvents().length).toBe(0);
```

### 2.6 Real-World Example: Risk Monitoring

```typescript
import { test, expect } from '@playwright/test';
import { SSETester } from '../helpers/sse-tester';

test('monitor risk alerts via SSE', async ({ page }) => {
  const sseTester = new SSETester(page, {
    connectTimeout: 5000,
  });

  try {
    // Connect to SSE endpoint
    await sseTester.connectSSE('http://localhost:8000/api/v1/sse/status');
    console.log('Connected to SSE status stream');

    // Listen for all events
    const eventLog: string[] = [];
    sseTester.onEvent((event) => {
      eventLog.push(`${event.event}: ${event.data}`);
      console.log(`[SSE] ${event.event}:`, event.data);
    });

    // Wait for risk alert
    const riskData = await sseTester.waitForData(
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

    console.log('Risk alert received:', riskData);

    // Verify risk alert structure
    expect(riskData).toHaveProperty('type', 'risk_alert');
    expect(riskData).toHaveProperty('severity');
    expect(riskData).toHaveProperty('message');
    expect(riskData).toHaveProperty('portfolio');

    // Check severity level
    const severity = (riskData as Record<string, unknown>).severity as string;
    expect(['low', 'medium', 'high', 'critical']).toContain(severity.toLowerCase());

    console.log('Risk monitoring test passed');
    console.log(`Total events received: ${eventLog.length}`);
  } finally {
    await sseTester.disconnect();
  }
});
```

---

## Part 3: Integration Patterns

### 3.1 Combined WebSocket + SSE Testing

```typescript
import { test, expect } from '@playwright/test';
import { WebSocketTester } from '../helpers/websocket-tester';
import { SSETester } from '../helpers/sse-tester';

test('test bidirectional WebSocket and unidirectional SSE together', async ({ page }) => {
  const wsTester = new WebSocketTester();
  const sseTester = new SSETester(page);

  try {
    // Connect both
    await wsTester.connectWebSocket('ws://localhost:8000/api/v1/ws/monitor');
    await sseTester.connectSSE('http://localhost:8000/api/v1/sse/updates');

    // Send command via WebSocket
    await wsTester.sendMessage({
      type: 'start_training',
      modelId: 'model-123',
    });

    // Listen for acknowledgment via WebSocket
    const ack = await wsTester.waitForMessage(
      (msg) => msg.type === 'acknowledge',
      3000,
    );
    expect(ack).toBeDefined();

    // Listen for progress updates via SSE
    const progressUpdate = await sseTester.waitForEvent('training_progress', 5000);
    expect(progressUpdate).toBeDefined();

    console.log('Bi-directional testing successful');
  } finally {
    await wsTester.disconnect();
    await sseTester.disconnect();
  }
});
```

### 3.2 Error Recovery Patterns

#### WebSocket Reconnection

```typescript
const wsTester = new WebSocketTester({
  autoReconnect: true,
  reconnectAttempts: 5,
  reconnectDelay: 1000,
});

// Errors are handled automatically
wsTester.onError((error) => {
  console.log('Connection error:', error.message);
});

// Register listener to detect reconnection
let reconnectCount = 0;
wsTester.onMessage((msg) => {
  if (msg.type === 'connection_restored') {
    reconnectCount++;
    console.log(`Reconnected (attempt #${reconnectCount})`);
  }
});
```

#### SSE Error Handling

```typescript
const sseTester = new SSETester(page, {
  autoReconnect: true,
});

sseTester.onError((error) => {
  console.log('SSE connection error:', error.message);
  // Error is automatically handled and reconnection attempted
});

// Assert that errors don't occur during critical operations
await sseTester.assertNoError();
```

### 3.3 High-Volume Message Testing

```typescript
test('handle high-frequency message updates', async () => {
  const wsTester = new WebSocketTester();

  await wsTester.connectWebSocket('ws://localhost:8000/api/v1/ws/tick-data');

  const messages: any[] = [];
  wsTester.onMessage((msg) => {
    messages.push(msg);
  });

  // Send subscription request
  await wsTester.sendMessage({
    type: 'subscribe',
    channel: 'tick_updates',
    symbols: ['AAPL', 'GOOGL', 'MSFT'],
  });

  // Collect messages for a time period
  await new Promise((resolve) => setTimeout(resolve, 5000));

  // Verify high message throughput
  console.log(`Received ${messages.length} tick updates in 5 seconds`);
  expect(messages.length).toBeGreaterThan(100);

  // Verify message ordering
  for (let i = 1; i < messages.length; i++) {
    const current = messages[i].data.timestamp;
    const previous = messages[i - 1].data.timestamp;
    expect(current).toBeGreaterThanOrEqual(previous);
  }

  await wsTester.disconnect();
});
```

---

## Part 4: Best Practices

### 4.1 Timeout Management

```typescript
// For fast, local connections
const fastConnectTimeout = 2000;

// For network calls or slower services
const networkTimeout = 5000;

// For user-driven operations that might take longer
const userActionTimeout = 10000;

// Apply appropriately
await wsTester.connectWebSocket(url, {
  connectTimeout: networkTimeout,
});

const message = await wsTester.waitForMessage(undefined, userActionTimeout);
```

### 4.2 Predicate Design

```typescript
// ❌ Too broad (matches many messages)
(msg) => msg.type === 'update'

// ✅ Better (specific to what you're testing)
(msg) => msg.type === 'training_progress' && msg.data.epoch > 5

// ✅ Best (comprehensive validation)
(msg) => {
  if (msg.type !== 'training_progress') return false;
  if (!msg.data?.epoch) return false;
  if (!msg.data?.accuracy) return false;
  return msg.data.accuracy > 0.85;
}
```

### 4.3 Resource Cleanup

```typescript
test.afterEach(async () => {
  // Always disconnect in cleanup
  if (wsTester.isConnectionActive()) {
    await wsTester.disconnect();
  }

  // Same for SSE
  if (sseTester.isConnectionActive()) {
    await sseTester.disconnect();
  }

  // For Playwright, close page
  await page.close();
});
```

### 4.4 Test Isolation

```typescript
test.describe('Real-Time Features', () => {
  let wsTester: WebSocketTester;

  test.beforeEach(() => {
    // Create fresh instance for each test
    wsTester = new WebSocketTester({
      connectTimeout: 5000,
      autoReconnect: false,
    });
  });

  test.afterEach(async () => {
    // Clean up after each test
    if (wsTester.isConnectionActive()) {
      await wsTester.disconnect();
    }
  });

  test('first test', async () => {
    // Test 1 with fresh wsTester
  });

  test('second test', async () => {
    // Test 2 with new fresh wsTester instance
  });
});
```

### 4.5 Debugging Tips

```typescript
// Enable detailed logging
wsTester.onMessage((msg) => {
  console.log('[WS Message]', JSON.stringify(msg, null, 2));
});

wsTester.onError((error) => {
  console.error('[WS Error]', error.stack);
});

sseTester.onEvent((event) => {
  console.log('[SSE Event]', event.event, event.data);
});

// Check current state
console.log('Active:', wsTester.isConnectionActive());
console.log('Messages:', wsTester.getMessages().length);

// Timeout helps identify slow responses
const slowMessage = await wsTester.waitForMessage(
  undefined,
  10000, // 10 second timeout shows slow response
);
```

---

## Part 5: Common Patterns and Examples

### 5.1 Subscribing to Channels

```typescript
// WebSocket channel subscription
await wsTester.connectWebSocket('ws://localhost:8000/api/v1/ws/data');

// Subscribe to multiple channels
await wsTester.sendMessage({
  type: 'subscribe',
  channels: ['training_progress', 'risk_alerts', 'model_metrics'],
});

// Receive updates from all channels
const update = await wsTester.waitForMessage(
  (msg) => ['training_progress', 'risk_alerts', 'model_metrics'].includes(msg.type),
  5000,
);
```

### 5.2 Request-Response Pattern

```typescript
// WebSocket request-response
await wsTester.connectWebSocket('ws://localhost:8000/api/v1/ws/rpc');

// Send request
await wsTester.sendMessage({
  id: '123',
  type: 'request',
  method: 'getModelStatus',
  params: { modelId: 'lstm-001' },
});

// Wait for response with matching ID
const response = await wsTester.waitForMessage(
  (msg) => msg.type === 'response' && msg.id === '123',
  5000,
);

console.log('Response:', response.data);
```

### 5.3 Stream Processing

```typescript
// Process a stream of events
await sseTester.connectSSE('http://localhost:8000/api/v1/sse/stream');

// Collect events for processing
const processedData: any[] = [];

sseTester.onEvent((event) => {
  try {
    const data = JSON.parse(event.data);
    // Transform and validate data
    if (data.value !== undefined && data.timestamp !== undefined) {
      processedData.push({
        timestamp: new Date(data.timestamp),
        value: data.value,
        source: event.event,
      });
    }
  } catch (e) {
    console.warn('Failed to parse event:', event.data);
  }
});

// Collect events for a time period
await new Promise((resolve) => setTimeout(resolve, 5000));

// Analyze collected data
console.log(`Processed ${processedData.length} events`);
```

---

## Part 6: API Reference

### WebSocketTester API

```typescript
class WebSocketTester {
  // Constructor
  constructor(options?: WebSocketOptions)

  // Connection
  async connectWebSocket(url: string, options?: Partial<WebSocketOptions>): Promise<void>
  async disconnect(): Promise<void>
  async waitForConnection(timeout?: number): Promise<void>

  // Messaging
  async sendMessage(message: unknown): Promise<void>
  async waitForMessage(
    predicate?: (msg: WebSocketMessage) => boolean,
    timeout?: number
  ): Promise<WebSocketMessage>
  async waitForMessages(count: number, timeout?: number): Promise<WebSocketMessage[]>

  // Listeners
  onMessage(listener: (message: WebSocketMessage) => void): void
  onError(listener: (error: Error) => void): void
  onClose(listener: () => void): void

  // Assertions
  async assertMessageReceived(type: string, timeout?: number): Promise<void>
  async assertMessageNotReceived(type: string, timeout?: number): Promise<void>
  async assertConnectionClosed(timeout?: number): Promise<void>
  assertConnected(): void

  // Utilities
  getMessages(): WebSocketMessage[]
  clearMessages(): void
  isConnectionActive(): boolean
}
```

### SSETester API

```typescript
class SSETester {
  // Constructor
  constructor(page: Page, options?: SSEOptions)

  // Connection
  async connectSSE(url: string, headers?: Record<string, string>): Promise<void>
  async disconnect(): Promise<void>

  // Events
  async waitForEvent(eventType: string, timeout?: number): Promise<SSEEvent>
  async waitForData(
    predicate?: (event: SSEEvent) => boolean,
    timeout?: number
  ): Promise<unknown>

  // Listeners
  onEvent(listener: (event: SSEEvent) => void): void
  onError(listener: (error: Error) => void): void
  onClose(listener: () => void): void

  // Assertions
  async assertEventReceived(eventType: string, timeout?: number): Promise<void>
  async assertDataMatches(pattern: RegExp | object, timeout?: number): Promise<void>
  async assertNoError(): Promise<void>

  // Utilities
  getEvents(): SSEEvent[]
  getEventsByType(eventType: string): SSEEvent[]
  clearEvents(): void
  isConnectionActive(): boolean
}
```

---

## Part 7: Troubleshooting

### Connection Issues

**Problem**: Connection timeout
```
Error: WebSocket connection timeout (5000ms)
```

**Solution**:
- Verify server is running on correct URL
- Increase timeout if server is slow
- Check network connectivity

### Message Not Received

**Problem**: Waiting for message that never arrives
```
Error: Message timeout (5000ms)
```

**Solution**:
- Verify subscription request was sent
- Check message type matches predicate
- Increase timeout for slow services
- Add logging to see actual messages received

### Reconnection Failures

**Problem**: Auto-reconnect not working
```
Error: WebSocket error: Connection failed
```

**Solution**:
- Verify `autoReconnect` is enabled
- Check `reconnectAttempts` limit
- Verify network is stable
- Review error listener logs

---

## Summary

Phase 4 Milestone 1 provides comprehensive tooling for testing real-time features:

- **WebSocket Testing**: Full bidirectional communication support
- **SSE Testing**: Unidirectional streaming with event filtering
- **Error Handling**: Timeout and reconnection management
- **Assertions**: Verify message receipt and data integrity
- **Best Practices**: Patterns for reliable real-time testing

**Next Steps**: Implement example tests for your real-time features using these utilities.

---

**Status**: ✅ Complete
**Last Updated**: 2025-12-05
**Maintainer**: Claude Code Testing Framework Team
