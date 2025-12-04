/**
 * Phase 4: WebSocket Real-Time Testing Helpers
 *
 * Comprehensive utilities for testing WebSocket connections, real-time data streams,
 * and bidirectional communication in E2E tests.
 *
 * @module tests/helpers/websocket-tester
 */

/**
 * Options for WebSocket connection
 */
export interface WebSocketOptions {
  /** Maximum time to wait for connection (ms) */
  connectTimeout?: number;
  /** Automatically reconnect on disconnect */
  autoReconnect?: boolean;
  /** Reconnection max attempts */
  reconnectAttempts?: number;
  /** Delay between reconnection attempts (ms) */
  reconnectDelay?: number;
}

/**
 * Message event from WebSocket
 */
export interface WebSocketMessage {
  /** Message type/event name */
  type: string;
  /** Message data */
  data?: unknown;
  /** Message payload */
  [key: string]: unknown;
}

/**
 * WebSocket tester for E2E testing
 *
 * Provides utilities for testing WebSocket connections, sending/receiving messages,
 * and asserting real-time data behavior.
 *
 * @example
 * ```typescript
 * const wsTester = new WebSocketTester();
 * await wsTester.connectWebSocket('ws://localhost:8000/api/v1/realtime');
 *
 * await wsTester.sendMessage({ type: 'subscribe', channel: 'training' });
 * const message = await wsTester.waitForMessage(m => m.type === 'training_progress');
 *
 * expect(message).toHaveProperty('progress');
 * await wsTester.disconnect();
 * ```
 */
export class WebSocketTester {
  private ws: WebSocket | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private messageListeners: Array<(msg: WebSocketMessage) => void> = [];
  private errorListeners: Array<(error: Error) => void> = [];
  private closeListeners: Array<() => void> = [];
  private connectionPromise: Promise<void> | null = null;
  private isConnected = false;
  private reconnectCount = 0;
  private options: Required<WebSocketOptions>;

  /**
   * Create a new WebSocket tester instance
   *
   * @param options - Connection options
   */
  constructor(options: WebSocketOptions = {}) {
    this.options = {
      connectTimeout: options.connectTimeout ?? 5000,
      autoReconnect: options.autoReconnect ?? false,
      reconnectAttempts: options.reconnectAttempts ?? 3,
      reconnectDelay: options.reconnectDelay ?? 1000,
    };
  }

  /**
   * Connect to a WebSocket server
   *
   * @param url - WebSocket URL (ws://... or wss://...)
   * @param options - Override default options for this connection
   * @throws Error if connection fails
   *
   * @example
   * ```typescript
   * await wsTester.connectWebSocket('ws://localhost:8000/api/realtime');
   * ```
   */
  public async connectWebSocket(
    url: string,
    options?: Partial<WebSocketOptions>,
  ): Promise<void> {
    if (this.ws) {
      await this.disconnect();
    }

    const mergedOptions = { ...this.options, ...options };
    this.options = mergedOptions as Required<WebSocketOptions>;

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(
        () => {
          reject(new Error(`WebSocket connection timeout (${this.options.connectTimeout}ms)`));
        },
        this.options.connectTimeout,
      );

      try {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          clearTimeout(timeout);
          this.isConnected = true;
          this.reconnectCount = 0;
          resolve();
        };

        this.ws.onmessage = (event: MessageEvent) => {
          try {
            const message = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
            this.messageQueue.push(message);
            this.messageListeners.forEach(listener => listener(message));
          } catch (error) {
            console.error('Failed to parse WebSocket message:', event.data);
          }
        };

        this.ws.onerror = (error: Event) => {
          clearTimeout(timeout);
          const wsError = new Error(`WebSocket error: ${error.type}`);
          this.errorListeners.forEach(listener => listener(wsError));
          reject(wsError);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          this.closeListeners.forEach(listener => listener());

          // Attempt reconnection if enabled
          if (
            this.options.autoReconnect &&
            this.reconnectCount < this.options.reconnectAttempts
          ) {
            this.reconnectCount++;
            setTimeout(() => {
              this.connectWebSocket(url, options).catch(console.error);
            }, this.options.reconnectDelay);
          }
        };
      } catch (error) {
        clearTimeout(timeout);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   *
   * @example
   * ```typescript
   * await wsTester.disconnect();
   * ```
   */
  public async disconnect(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.ws) {
        resolve();
        return;
      }

      this.isConnected = false;

      // Set a timeout to force close
      const timeout = setTimeout(() => {
        this.ws = null;
        resolve();
      }, 1000);

      try {
        this.ws.close();
        timeout; // Clear timeout after close
        this.ws = null;
        resolve();
      } catch (error) {
        this.ws = null;
        resolve();
      }
    });
  }

  /**
   * Wait for WebSocket connection to be established
   *
   * @param timeout - Maximum time to wait (ms)
   * @throws Error if timeout expires before connection
   */
  public async waitForConnection(timeout: number = this.options.connectTimeout): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnected) {
        resolve();
        return;
      }

      const timer = setTimeout(
        () => reject(new Error(`Connection timeout (${timeout}ms)`)),
        timeout,
      );

      const checkConnection = setInterval(() => {
        if (this.isConnected) {
          clearInterval(checkConnection);
          clearTimeout(timer);
          resolve();
        }
      }, 50);
    });
  }

  /**
   * Send a message through WebSocket
   *
   * @param message - Message object to send (will be JSON stringified)
   * @throws Error if WebSocket is not connected
   *
   * @example
   * ```typescript
   * await wsTester.sendMessage({
   *   type: 'subscribe',
   *   channel: 'training_progress',
   *   modelId: 'lstm-001'
   * });
   * ```
   */
  public async sendMessage(message: unknown): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    try {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      this.ws.send(payload);
    } catch (error) {
      throw new Error(`Failed to send WebSocket message: ${error}`);
    }
  }

  /**
   * Wait for a single message matching optional predicate
   *
   * @param predicate - Optional function to filter messages
   * @param timeout - Maximum time to wait (ms)
   * @returns The matching message
   * @throws Error if timeout expires before message received
   *
   * @example
   * ```typescript
   * const message = await wsTester.waitForMessage(
   *   m => m.type === 'training_progress' && m.progress >= 50
   * );
   * ```
   */
  public async waitForMessage(
    predicate?: (msg: WebSocketMessage) => boolean,
    timeout: number = 5000,
  ): Promise<WebSocketMessage> {
    // Check existing messages in queue
    if (predicate) {
      const existing = this.messageQueue.find(predicate);
      if (existing) {
        return existing;
      }
    } else if (this.messageQueue.length > 0) {
      return this.messageQueue.shift()!;
    }

    // Wait for new message
    return new Promise((resolve, reject) => {
      const timer = setTimeout(
        () => reject(new Error(`Message timeout (${timeout}ms)`)),
        timeout,
      );

      const listener = (message: WebSocketMessage) => {
        if (!predicate || predicate(message)) {
          clearTimeout(timer);
          this.messageListeners = this.messageListeners.filter(l => l !== listener);
          resolve(message);
        }
      };

      this.messageListeners.push(listener);
    });
  }

  /**
   * Wait for multiple messages matching optional predicate
   *
   * @param count - Number of messages to wait for
   * @param timeout - Maximum time to wait (ms)
   * @returns Array of messages
   * @throws Error if timeout expires before all messages received
   *
   * @example
   * ```typescript
   * const updates = await wsTester.waitForMessages(5, 10000);
   * ```
   */
  public async waitForMessages(count: number, timeout: number = 10000): Promise<WebSocketMessage[]> {
    const messages: WebSocketMessage[] = [];

    for (let i = 0; i < count; i++) {
      const message = await this.waitForMessage(undefined, timeout);
      messages.push(message);
    }

    return messages;
  }

  /**
   * Register a listener for incoming messages
   *
   * @param listener - Function called for each message
   *
   * @example
   * ```typescript
   * wsTester.onMessage((message) => {
   *   console.log('Received:', message);
   * });
   * ```
   */
  public onMessage(listener: (message: WebSocketMessage) => void): void {
    this.messageListeners.push(listener);
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
   * Assert that a message of given type was received
   *
   * @param type - Expected message type
   * @param timeout - Maximum time to wait (ms)
   * @throws Error if message not received within timeout
   *
   * @example
   * ```typescript
   * await wsTester.assertMessageReceived('training_progress', 5000);
   * ```
   */
  public async assertMessageReceived(type: string, timeout: number = 5000): Promise<void> {
    try {
      await this.waitForMessage(m => m.type === type, timeout);
    } catch (error) {
      throw new Error(`Expected message of type '${type}' was not received`);
    }
  }

  /**
   * Assert that a message of given type was NOT received
   *
   * @param type - Message type that should not be received
   * @param timeout - Time to wait for message (ms)
   *
   * @example
   * ```typescript
   * await wsTester.assertMessageNotReceived('error', 2000);
   * ```
   */
  public async assertMessageNotReceived(type: string, timeout: number = 2000): Promise<void> {
    try {
      await this.waitForMessage(m => m.type === type, timeout);
      throw new Error(`Message of type '${type}' was received when it should not have been`);
    } catch (error) {
      // Expected - message should not be received
      if ((error as Error).message.includes('timeout')) {
        return; // Timeout is expected
      }
      throw error;
    }
  }

  /**
   * Assert that WebSocket connection is closed
   *
   * @param timeout - Maximum time to wait for close (ms)
   * @throws Error if connection does not close
   */
  public async assertConnectionClosed(timeout: number = 5000): Promise<void> {
    if (!this.isConnected && !this.ws) {
      return; // Already closed
    }

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Connection did not close within ${timeout}ms`));
      }, timeout);

      const listener = () => {
        clearTimeout(timer);
        this.closeListeners = this.closeListeners.filter(l => l !== listener);
        resolve();
      };

      this.closeListeners.push(listener);
    });
  }

  /**
   * Assert that WebSocket connection is open
   *
   * @throws Error if not connected
   */
  public assertConnected(): void {
    if (!this.isConnected) {
      throw new Error('WebSocket is not connected');
    }
  }

  /**
   * Get all messages received since connection
   *
   * @returns Array of messages
   */
  public getMessages(): WebSocketMessage[] {
    return [...this.messageQueue];
  }

  /**
   * Clear message queue
   */
  public clearMessages(): void {
    this.messageQueue = [];
  }

  /**
   * Get current connection status
   *
   * @returns true if connected, false otherwise
   */
  public isConnectionActive(): boolean {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN;
  }
}

/**
 * Create a WebSocket tester instance with default options
 *
 * @returns New WebSocketTester instance
 */
export function createWebSocketTester(): WebSocketTester {
  return new WebSocketTester();
}

export default {
  WebSocketTester,
  createWebSocketTester,
};
