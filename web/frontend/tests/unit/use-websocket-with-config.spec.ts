import { beforeEach, describe, expect, it, vi } from 'vitest'

const cleanup = vi.fn()
const registerSubscription = vi.fn(() => cleanup)
const subscribe = vi.fn(() => registerSubscription)
const unsubscribe = vi.fn()

vi.mock('@/composables/useWebSocketEnhanced', () => ({
  useWebSocket: vi.fn(() => ({
    connectionState: { value: 'connected' },
    isConnected: { value: true },
    lastMessage: { value: null },
    error: { value: null },
    connect: vi.fn(),
    disconnect: vi.fn(),
    subscribe,
    unsubscribe,
    send: vi.fn(),
    getActiveSubscriptions: vi.fn(() => []),
    getSubscriberCount: vi.fn(() => 0)
  }))
}))

const pageConfig = {
  dashboard: {
    type: 'page',
    routePath: 'dashboard',
    title: '交易室',
    description: '交易室概览',
    apiEndpoint: '/api/v1/market/*',
    wsChannel: 'dashboard:realtime',
    component: 'ArtDecoDashboard.vue',
    requiresAuth: true
  },
  tradePositions: {
    type: 'page',
    routePath: 'positions',
    title: '头寸管理',
    description: '头寸管理',
    apiEndpoint: '/api/v1/trade/positions',
    wsChannel: 'trade:positions',
    component: 'ArtDecoTradingPositions.vue',
    requiresAuth: true
  }
}

vi.mock('@/config/pageConfig', () => ({
  PAGE_CONFIG: pageConfig,
  getPageConfig: (routeName: keyof typeof pageConfig) => pageConfig[routeName] ?? null,
  isRouteName: (routeName: string) => routeName in pageConfig,
  isStandardConfig: (config: { wsChannel?: string } | null | undefined) => Boolean(config?.wsChannel)
}))

describe('useWebSocketWithConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    subscribe.mockReturnValue(registerSubscription)
    registerSubscription.mockReturnValue(cleanup)
  })

  it('subscribes immediately for a configured route and returns the cleanup callback', async () => {
    const { useWebSocketWithConfig } = await import('@/composables/useWebSocketWithConfig')
    const callback = vi.fn()

    const teardown = useWebSocketWithConfig().subscribeByRoute('dashboard', callback)

    expect(subscribe).toHaveBeenCalledWith('dashboard:realtime', callback)
    expect(registerSubscription).toHaveBeenCalledTimes(1)
    expect(teardown).toBe(cleanup)
  })

  it('subscribes every configured route immediately in batch mode', async () => {
    const tradeCleanup = vi.fn()
    subscribe
      .mockReturnValueOnce(registerSubscription)
      .mockReturnValueOnce(vi.fn(() => tradeCleanup))

    const { useWebSocketWithConfig } = await import('@/composables/useWebSocketWithConfig')
    const callback = vi.fn()

    const teardownAll = useWebSocketWithConfig().subscribeAllWebSocketRoutes(callback)

    expect(subscribe).toHaveBeenNthCalledWith(1, 'dashboard:realtime', callback)
    expect(subscribe).toHaveBeenNthCalledWith(2, 'trade:positions', callback)
    expect(registerSubscription).toHaveBeenCalledTimes(1)

    teardownAll()

    expect(cleanup).toHaveBeenCalledTimes(1)
    expect(tradeCleanup).toHaveBeenCalledTimes(1)
  })

  it('keeps the legacy utils import path compatible with the composables module', async () => {
    const composablesModule = await import('@/composables/useWebSocketWithConfig')
    const legacyModule = await import('@/utils/useWebSocketWithConfig')

    expect(legacyModule.useWebSocketWithConfig).toBe(composablesModule.useWebSocketWithConfig)
  })
})
