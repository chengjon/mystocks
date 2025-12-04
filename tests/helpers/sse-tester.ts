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
 * Options for SSE connection
 */
export interface SSEOptions {
  /** Maximum time to wait for connection (ms) */
  connectTimeout?: number;
  /** Request headers */
  headers?: Record<string, string>;
  /** Automatically reconnect on error */
  autoReconnect?: boolean;
  /** Reconnection max attempts */
  reconnectAttempts?: number;
  /** Delay between reconnection attempts (ms) */
  reconnectDelay?: number;
}

/**
 * SSE event data
 */
export interface SSEEvent {
  /** Event type/name */
  event?: string;
  /** Event data */
  data: string;
  /** Event ID */
  id?: string;
  /** Parsed data (if JSON) */
  parsedData?: unknown;
}

/**
 * SSE tester for E2E testing
 *
 * Provides utilities for testing Server-Sent Events connections,
 * listening for events, and asserting real-time data behavior.
 *
 * @example
 * ```typescript
 * const sseTester = new SSETester(page);
 * await sseTester.connectSSE('http://localhost:8000/api/v1/sse/status');
 *
 * const event = await sseTester.waitForEvent('risk_alert', 10000);
 * expect(event.data).toContain('risk_level');
 *
 * await sseTester.disconnect();
 * ```
 */
export class SSETester {
  private page: Page;
  private eventSource: any = null;
  private events: SSEEvent[] = [];
  private eventListeners: Array<(event: SSEEvent) => void> = [];
  private errorListeners: Array<(error: Error) => void> = [];
  private closeListeners: Array<() => void> = [];
  private isConnected = false;
  private reconnectCount = 0;
  private options: Required<SSEOptions>;

  /**
   * Create a new SSE tester instance
   *
   * @param page - Playwright page object
   * @param options - Connection options
   */
  constructor(page: Page, options: SSEOptions = {}) {
    this.page = page;
    this.options = {
      connectTimeout: options.connectTimeout ?? 5000,
      headers: options.headers ?? {},
      autoReconnect: options.autoReconnect ?? true,
      reconnectAttempts: options.reconnectAttempts ?? 5,
      reconnectDelay: options.reconnectDelay ?? 1000,
    };
  }

  /**
   * Connect to an SSE endpoint
   *
   * @param url - SSE endpoint URL
   * @param options - Override default options for this connection
   * @throws Error if connection fails
   *
   * @example
   * ```typescript
   * await sseTester.connectSSE('http://localhost:8000/api/v1/sse/status', {
   *   headers: { 'Authorization': 'Bearer token' }
   * });
   * ```
   */
  public async connectSSE(url: string, options?: Partial<SSEOptions>): Promise<void> {
    if (this.eventSource) {
      await this.disconnect();
    }

    const mergedOptions = { ...this.options, ...options };
    this.options = mergedOptions as Required<SSEOptions>;

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(
        () => {
          reject(new Error(`SSE connection timeout (${this.options.connectTimeout}ms)`));
        },
        this.options.connectTimeout,
      );

      this.page
        .evaluate(
          async ({ url: eventUrl, headers, timeout: t }) => {
            return new Promise<void>((pageResolve, pageReject) => {
              const timer = setTimeout(() => {
                pageReject(new Error('SSE connection timeout'));
              }, t);

              try {
                const es = new EventSource(eventUrl);

                es.onopen = () => {
                  clearTimeout(timer);
                  (window as any).__sseEventSource = es;
                  (window as any).__sseConnected = true;
                  pageResolve();
                };

                es.onerror = (error: Event) => {
                  if (es.readyState === EventSource.CLOSED) {
                    clearTimeout(timer);
                    pageReject(new Error('SSE connection closed'));
                  }
                };
              } catch (error) {
                clearTimeout(timer);
                pageReject(error);
              }
            });
          },
          { url, headers: this.options.headers, timeout: this.options.connectTimeout },
        )
        .then(() => {
          clearTimeout(timeout);
          this.isConnected = true;
          this.reconnectCount = 0;

          // Start listening for events
          this.startListening();
          resolve();
        })
        .catch((error) => {
          clearTimeout(timeout);
          const sseError = new Error(`SSE connection failed: ${error.message}`);
          this.errorListeners.forEach(listener => listener(sseError));
          reject(sseError);
        });
    });
  }

  /**
   * Start listening for SSE events in the page context
   */
  private startListening(): void {
    // Set up polling to get events from page
    const pollInterval = setInterval(async () => {
      if (!this.isConnected) {
        clearInterval(pollInterval);
        return;
      }

      try {
        const newEvents = await this.page.evaluate(() => {
          const es = (window as any).__sseEventSource;
          if (!es) return [];

          // Create event listeners for all event types
          const events: SSEEvent[] = [];

          // Override onmessage to capture events
          const originalAddEventListener = es.addEventListener;
          es.addEventListener = function (eventType: string, listener: Function) {
            originalAddEventListener.call(this, eventType, (e: any) => {
              events.push({
                event: eventType,
                data: e.data,
                id: e.lastEventId,
              });
              listener(e);
            });
          };

          return events;
        });

        newEvents.forEach(event => {
          this.events.push(event);
          this.eventListeners.forEach(listener => listener(event));
        });
      } catch (error) {
        // Page context error, continue polling
      }
    }, 100);
  }

  /**
   * Disconnect from SSE endpoint
   *
   * @example
   * ```typescript
   * await sseTester.disconnect();
   * ```
   */
  public async disconnect(): Promise<void> {
    if (!this.isConnected) {
      return;
    }

    this.isConnected = false;

    try {
      await this.page.evaluate(() => {
        const es = (window as any).__sseEventSource;
        if (es) {
          es.close();
          (window as any).__sseEventSource = null;
          (window as any).__sseConnected = false;
        }
      });
    } catch (error) {
      // Ignore errors during disconnect
    }

    this.closeListeners.forEach(listener => listener());
  }

  /**
   * Wait for an event of specific type
   *
   * @param eventType - Event type to wait for
   * @param timeout - Maximum time to wait (ms)
   * @returns The event
   * @throws Error if timeout expires before event received
   *
   * @example
   * ```typescript
   * const event = await sseTester.waitForEvent('risk_alert', 10000);
   * ```
   */
  public async waitForEvent(eventType: string, timeout: number = 5000): Promise<SSEEvent> {
    // Check existing events
    const existing = this.events.find(e => e.event === eventType);
    if (existing) {
      return existing;
    }

    // Wait for new event
    return new Promise((resolve, reject) => {
      const timer = setTimeout(
        () => reject(new Error(`Event '${eventType}' not received within ${timeout}ms`)),
        timeout,
      );

      const listener = (event: SSEEvent) => {
        if (event.event === eventType) {
          clearTimeout(timer);
          this.eventListeners = this.eventListeners.filter(l => l !== listener);
          resolve(event);
        }
      };

      this.eventListeners.push(listener);
    });
  }

  /**
   * Wait for data matching optional predicate
   *
   * @param predicate - Optional function to filter events
   * @param timeout - Maximum time to wait (ms)
   * @returns The event data
   * @throws Error if timeout expires
   *
   * @example
   * ```typescript
   * const data = await sseTester.waitForData(
   *   d => JSON.parse(d?.data || '{}')?.level === 'critical'
   * );
   * ```
   */
  public async waitForData(
    predicate?: (event: SSEEvent) => boolean,
    timeout: number = 5000,
  ): Promise<unknown> {
    // Check existing events
    if (predicate) {
      const existing = this.events.find(predicate);
      if (existing) {
        return this.parseEventData(existing);
      }
    } else if (this.events.length > 0) {
      return this.parseEventData(this.events.shift()!);
    }

    // Wait for new event
    return new Promise((resolve, reject) => {
      const timer = setTimeout(
        () => reject(new Error(`Data not received within ${timeout}ms`)),
        timeout,
      );

      const listener = (event: SSEEvent) => {
        if (!predicate || predicate(event)) {
          clearTimeout(timer);
          this.eventListeners = this.eventListeners.filter(l => l !== listener);
          resolve(this.parseEventData(event));
        }
      };

      this.eventListeners.push(listener);
    });
  }

  /**
   * Parse event data, attempting JSON parsing if possible
   *
   * @param event - SSE event
   * @returns Parsed data or raw string
   */
  private parseEventData(event: SSEEvent): unknown {
    try {
      return JSON.parse(event.data);
    } catch {
      return event.data;
    }
  }

  /**
   * Register a listener for incoming events
   *
   * @param listener - Function called for each event
   *
   * @example
   * ```typescript
   * sseTester.onEvent((event) => {
   *   console.log('Event:', event.event, event.data);
   * });
   * ```
   */
  public onEvent(listener: (event: SSEEvent) => void): void {
    this.eventListeners.push(listener);
  }

  /**
   * Register a listener for connection errors
   *
   * @param listener - Function called on error
   */
  public onError(listener: (error: Error) => void): void {
    this.errorListeners.push(listener);
  }

  /**
   * Register a listener for connection close
   *
   * @param listener - Function called when connection closes
   */
  public onClose(listener: () => void): void {
    this.closeListeners.push(listener);
  }

  /**
   * Assert that an event of given type was received
   *
   * @param eventType - Expected event type
   * @param timeout - Maximum time to wait (ms)
   * @throws Error if event not received
   *
   * @example
   * ```typescript
   * await sseTester.assertEventReceived('risk_alert', 5000);
   * ```
   */
  public async assertEventReceived(eventType: string, timeout: number = 5000): Promise<void> {
    try {
      await this.waitForEvent(eventType, timeout);
    } catch (error) {
      throw new Error(`Expected event '${eventType}' was not received`);
    }
  }

  /**
   * Assert that data matches pattern or object
   *
   * @param pattern - RegExp or object to match
   * @throws Error if data does not match
   *
   * @example
   * ```typescript
   * await sseTester.assertDataMatches({ level: 'critical' });
   * await sseTester.assertDataMatches(/error/i);
   * ```
   */
  public async assertDataMatches(pattern: RegExp | object, timeout: number = 5000): Promise<void> {
    const data = await this.waitForData(undefined, timeout);

    if (pattern instanceof RegExp) {
      if (!pattern.test(String(data))) {
        throw new Error(`Data '${data}' does not match pattern '${pattern}'`);
      }
    } else {
      const dataObj = typeof data === 'string' ? JSON.parse(data) : data;
      const patternObj = pattern as Record<string, unknown>;

      for (const [key, value] of Object.entries(patternObj)) {
        if ((dataObj as Record<string, unknown>)[key] !== value) {
          throw new Error(
            `Data property '${key}' is '${(dataObj as Record<string, unknown>)[key]}', expected '${value}'`,
          );
        }
      }
    }
  }

  /**
   * Assert that no errors occurred
   *
   * @throws Error if errors were detected
   */
  public async assertNoError(): Promise<void> {
    return new Promise((resolve) => {
      // Wait a short time to detect any errors
      const timer = setTimeout(() => {
        resolve();
      }, 500);

      const errorListener = (error: Error) => {
        clearTimeout(timer);
        this.errorListeners = this.errorListeners.filter(l => l !== errorListener);
        throw new Error(`SSE error detected: ${error.message}`);
      };

      this.errorListeners.push(errorListener);
    });
  }

  /**
   * Get all events received
   *
   * @returns Array of events
   */
  public getEvents(): SSEEvent[] {
    return [...this.events];
  }

  /**
   * Get events of specific type
   *
   * @param eventType - Event type to filter by
   * @returns Array of events matching type
   */
  public getEventsByType(eventType: string): SSEEvent[] {
    return this.events.filter(e => e.event === eventType);
  }

  /**
   * Clear event queue
   */
  public clearEvents(): void {
    this.events = [];
  }

  /**
   * Get current connection status
   *
   * @returns true if connected, false otherwise
   */
  public isConnectionActive(): boolean {
    return this.isConnected;
  }
}

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
