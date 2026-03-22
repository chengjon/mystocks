import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { WebSocketManager, WebSocketState } from '@/utils/webSocketManager'

const { socketInstances, MockWebSocket } = vi.hoisted(() => {
  const socketInstances: Array<{
    url: string
    protocols?: string[]
    send: ReturnType<typeof vi.fn>
    close: ReturnType<typeof vi.fn>
    readyState: number
    binaryType: string
    onopen: ((event: Event) => void) | null
    onmessage: ((event: MessageEvent) => void) | null
    onclose: ((event: CloseEvent) => void) | null
    onerror: ((event: Event) => void) | null
  }> = []

  class MockWebSocket {
    static CONNECTING = 0
    static OPEN = 1
    static CLOSING = 2
    static CLOSED = 3

    url: string
    protocols?: string[]
    send = vi.fn()
    close = vi.fn((code?: number, reason?: string) => {
      this.readyState = MockWebSocket.CLOSED
      if (code !== undefined) {
        this.onclose?.({ code, reason: reason ?? '' } as CloseEvent)
      }
    })
    readyState = MockWebSocket.CONNECTING
    binaryType = 'blob'
    onopen: ((event: Event) => void) | null = null
    onmessage: ((event: MessageEvent) => void) | null = null
    onclose: ((event: CloseEvent) => void) | null = null
    onerror: ((event: Event) => void) | null = null

    constructor(url: string, protocols?: string[]) {
      this.url = url
      this.protocols = protocols
      socketInstances.push(this)
    }
  }

  return { socketInstances, MockWebSocket }
})

Object.defineProperty(globalThis, 'WebSocket', {
  value: MockWebSocket,
  configurable: true
})

const getLastSocket = () => {
  const socket = socketInstances.at(-1)
  expect(socket).toBeDefined()
  return socket!
}

describe('WebSocketManager', () => {
  let wsManager: WebSocketManager

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    socketInstances.length = 0
    wsManager = new WebSocketManager({
      url: 'ws://localhost:8080',
      reconnectAttempts: 3,
      reconnectInterval: 1000,
      heartbeatInterval: 30000
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
      const socket = getLastSocket()

      socket.readyState = MockWebSocket.OPEN
      socket.onopen?.(new Event('open'))
      await connectPromise

      expect(wsManager.getState()).toBe(WebSocketState.CONNECTED)
      expect(wsManager.isConnected()).toBe(true)
    })

    it('should handle connection failure', async () => {
      const connectPromise = wsManager.connect()
      const socket = getLastSocket()

      socket.onerror?.(new Event('error'))

      await expect(connectPromise).rejects.toBeInstanceOf(Event)
      expect(wsManager.getState()).toBe(WebSocketState.ERROR)
    })

    it('should disconnect properly', async () => {
      const connectPromise = wsManager.connect()
      const socket = getLastSocket()
      socket.readyState = MockWebSocket.OPEN
      socket.onopen?.(new Event('open'))
      await connectPromise

      wsManager.disconnect()

      expect(socket.close).toHaveBeenCalledWith(1000, 'Client disconnect')
      expect(wsManager.getState()).toBe(WebSocketState.DISCONNECTED)
    })
  })

  describe('Message Handling', () => {
    it('should send messages when connected', async () => {
      const connectPromise = wsManager.connect()
      const socket = getLastSocket()
      socket.readyState = MockWebSocket.OPEN
      socket.onopen?.(new Event('open'))
      await connectPromise

      const message = { type: 'test', data: 'hello' }
      const result = wsManager.send(message)

      expect(result).toBe(true)
      expect(socket.send).toHaveBeenCalledTimes(1)
      const payload = JSON.parse(socket.send.mock.calls[0][0])
      expect(payload).toMatchObject(message)
      expect(typeof payload.timestamp).toBe('number')
      expect(typeof payload.id).toBe('string')
    })

    it('should not send messages when disconnected', () => {
      const message = { type: 'test', data: 'hello' }
      const result = wsManager.send(message)

      expect(result).toBe(false)
    })

    it('should handle incoming messages', async () => {
      const connectPromise = wsManager.connect()
      const socket = getLastSocket()
      socket.readyState = MockWebSocket.OPEN
      socket.onopen?.(new Event('open'))
      await connectPromise

      const mockHandler = vi.fn()
      wsManager.on('test-event', mockHandler)

      socket.onmessage?.({
        data: JSON.stringify({ type: 'test-event', data: 'test data' })
      } as MessageEvent)

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

      wsManager['emit']('custom-event', { type: 'custom-event', data: { data: 'test' } })

      expect(mockHandler).toHaveBeenCalledWith({ type: 'custom-event', data: { data: 'test' } })
    })

    it('should unregister event handlers', () => {
      const mockHandler = vi.fn()
      wsManager.on('custom-event', mockHandler)
      wsManager.off('custom-event', mockHandler)

      wsManager['emit']('custom-event', { type: 'custom-event', data: { data: 'test' } })

      expect(mockHandler).not.toHaveBeenCalled()
    })

    it('should handle connection state change handlers', () => {
      const mockHandler = vi.fn()
      wsManager.onStateChange(mockHandler)

      wsManager['updateState'](WebSocketState.CONNECTED)

      expect(mockHandler).toHaveBeenCalledWith(WebSocketState.CONNECTED)
    })
  })

  describe('Reconnection Logic', () => {
    it('should attempt reconnection on abnormal closure', async () => {
      const connectPromise = wsManager.connect()
      const socket = getLastSocket()
      socket.readyState = MockWebSocket.OPEN
      socket.onopen?.(new Event('open'))
      await connectPromise

      socket.onclose?.({ code: 1006, reason: 'Abnormal closure' } as CloseEvent)
      await vi.advanceTimersByTimeAsync(1000)

      expect(socketInstances.length).toBe(2)
      expect(wsManager.getState()).toBe(WebSocketState.CONNECTING)
    })

    it('should stop reconnection after max attempts', () => {
      const limitedManager = new WebSocketManager({
        url: 'ws://localhost:8080',
        reconnectAttempts: 0,
        reconnectInterval: 100
      })

      limitedManager['attemptReconnect']()

      expect(limitedManager.getState()).toBe(WebSocketState.DISCONNECTED)
    })
  })

  describe('Heartbeat', () => {
    it('should send heartbeat messages when connected', async () => {
      const connectPromise = wsManager.connect()
      const socket = getLastSocket()
      socket.readyState = MockWebSocket.OPEN
      socket.onopen?.(new Event('open'))
      await connectPromise

      await vi.advanceTimersByTimeAsync(30000)

      expect(socket.send).toHaveBeenCalledTimes(1)
      const payload = JSON.parse(socket.send.mock.calls[0][0])
      expect(payload.type).toBe('heartbeat')
      expect(typeof payload.timestamp).toBe('number')
      expect(typeof payload.id).toBe('string')
    })
  })
})
