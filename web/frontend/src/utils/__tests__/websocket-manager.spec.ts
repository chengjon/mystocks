import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { WebSocketManager, WebSocketState } from '@/utils/webSocketManager'

// Mock WebSocket
const mockWebSocket = {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
  send: vi.fn(),
  close: vi.fn(),
  readyState: 0,
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3
}

global.WebSocket = vi.fn().mockImplementation(() => mockWebSocket)

describe('WebSocketManager', () => {
  let wsManager: WebSocketManager

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    wsManager = new WebSocketManager({
      url: 'ws://localhost:8080',
      reconnectAttempts: 3,
      reconnectInterval: 1000
    })
  })

  afterEach(() => {
    wsManager.disconnect()
    vi.useRealTimers()
  })

  describe('Connection Management', () => {
    it('should initialize with correct default config', () => {
      expect(wsManager.getState()).toBe(WebSocketState.DISCONNECTED)
    })

    it('should connect successfully', async () => {
      const connectPromise = wsManager.connect()

      // Simulate successful connection
      const openEvent = new Event('open')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'open')[1](openEvent)

      await connectPromise

      expect(wsManager.getState()).toBe(WebSocketState.CONNECTED)
      expect(wsManager.isConnected()).toBe(true)
    })

    it('should handle connection failure', async () => {
      const connectPromise = wsManager.connect()

      // Simulate connection error
      const errorEvent = new Event('error')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'error')[1](errorEvent)

      await expect(connectPromise).rejects.toThrow()
      expect(wsManager.getState()).toBe(WebSocketState.ERROR)
    })

    it('should disconnect properly', () => {
      // First connect
      wsManager.connect()
      const openEvent = new Event('open')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'open')[1](openEvent)

      // Then disconnect
      wsManager.disconnect()

      expect(mockWebSocket.close).toHaveBeenCalledWith(1000, 'Client disconnect')
      expect(wsManager.getState()).toBe(WebSocketState.DISCONNECTED)
    })
  })

  describe('Message Handling', () => {
    it('should send messages when connected', () => {
      // Connect first
      wsManager.connect()
      const openEvent = new Event('open')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'open')[1](openEvent)

      const message = { type: 'test', data: 'hello' }
      const result = wsManager.send(message)

      expect(result).toBe(true)
      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify({
        ...message,
        timestamp: expect.any(Number),
        id: expect.any(String)
      }))
    })

    it('should not send messages when disconnected', () => {
      const message = { type: 'test', data: 'hello' }
      const result = wsManager.send(message)

      expect(result).toBe(false)
      expect(mockWebSocket.send).not.toHaveBeenCalled()
    })

    it('should handle incoming messages', () => {
      // Connect first
      wsManager.connect()
      const openEvent = new Event('open')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'open')[1](openEvent)

      const mockHandler = vi.fn()
      wsManager.on('test-event', mockHandler)

      // Simulate incoming message
      const messageEvent = {
        data: JSON.stringify({ type: 'test-event', data: 'test data' })
      }
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'message')[1](messageEvent)

      expect(mockHandler).toHaveBeenCalledWith({
        type: 'test-event',
        data: 'test data'
      })
    })
  })

  describe('Event Handling', () => {
    it('should register and trigger event handlers', () => {
      const mockHandler = vi.fn()
      wsManager.on('custom-event', mockHandler)

      // Simulate event emission
      wsManager['emit']('custom-event', { data: 'test' })

      expect(mockHandler).toHaveBeenCalledWith({ data: 'test' })
    })

    it('should unregister event handlers', () => {
      const mockHandler = vi.fn()
      wsManager.on('custom-event', mockHandler)
      wsManager.off('custom-event', mockHandler)

      wsManager['emit']('custom-event', { data: 'test' })

      expect(mockHandler).not.toHaveBeenCalled()
    })

    it('should handle connection state change handlers', () => {
      const mockHandler = vi.fn()
      wsManager.onStateChange(mockHandler)

      // Trigger state change
      wsManager['updateState'](WebSocketState.CONNECTED)

      expect(mockHandler).toHaveBeenCalledWith(WebSocketState.CONNECTED)
    })
  })

  describe('Reconnection Logic', () => {
    it('should attempt reconnection on abnormal closure', async () => {
      // Connect first
      const connectPromise = wsManager.connect()
      const openEvent = new Event('open')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'open')[1](openEvent)
      await connectPromise

      // Simulate abnormal closure
      const closeEvent = { code: 1006, reason: 'Abnormal closure' }
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'close')[1](closeEvent)

      // Fast-forward timers
      await vi.advanceTimersByTime(1000)

      expect(global.WebSocket).toHaveBeenCalledTimes(2) // Original + reconnect
    })

    it('should stop reconnection after max attempts', async () => {
      wsManager = new WebSocketManager({
        url: 'ws://localhost:8080',
        reconnectAttempts: 2,
        reconnectInterval: 100
      })

      // Connect and fail multiple times
      for (let i = 0; i < 3; i++) {
        const connectPromise = wsManager.connect()
        const errorEvent = new Event('error')
        mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'error')[1](errorEvent)

        try {
          await connectPromise
        } catch {
          // Expected to fail
        }
      }

      expect(wsManager.getState()).toBe(WebSocketState.DISCONNECTED)
    })
  })

  describe('Heartbeat', () => {
    it('should send heartbeat messages when connected', async () => {
      // Connect
      const connectPromise = wsManager.connect()
      const openEvent = new Event('open')
      mockWebSocket.addEventListener.mock.calls.find(call => call[0] === 'open')[1](openEvent)
      await connectPromise

      // Fast-forward time for heartbeat
      await vi.advanceTimersByTime(31000) // More than default 30s interval

      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'heartbeat',
        timestamp: expect.any(Number),
        id: expect.any(String)
      }))
    })
  })
})