import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ArtDecoDashboard from '@/views/artdeco-pages/ArtDecoDashboard.vue'
import dashboardService from '@/api/services/dashboardService'
import { marketService } from '@/api/services/marketService'
import { mockWebSocket } from '@/api/mockWebSocket'

vi.mock('@/api/services/dashboardService', () => ({
  default: {
    getMarketOverview: vi.fn().mockResolvedValue({ data: [] }),
    getFundFlow: vi.fn().mockResolvedValue({ data: {} }),
    getIndustryFlow: vi.fn().mockResolvedValue({ data: [] }),
    getStockFlowRanking: vi.fn().mockResolvedValue({ data: [] }),
    getActiveStrategies: vi.fn().mockResolvedValue({ data: [] }),
    getPositionRisk: vi.fn().mockResolvedValue({ data: { totalPnL: 0 } }),
    getSystemHealth: vi.fn().mockResolvedValue({ data: [] }),
    getTechnicalIndicators: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/api/services/marketService', () => ({
  marketService: {
    getKline: vi.fn().mockResolvedValue({ data: [] })
  }
}))

const wsMock = vi.hoisted(() => {
  let trendHandler: ((payload: unknown) => void) | null = null
  const unsubscribeTrend = vi.fn()

  return {
    subscribe: vi.fn((_topic: string, handler: (payload: unknown) => void) => {
      trendHandler = handler
    }),
    unsubscribe: vi.fn(() => unsubscribeTrend()),
    unsubscribeTrend,
    getTrendHandler: () => trendHandler,
    reset: () => {
      trendHandler = null
      unsubscribeTrend.mockReset()
    }
  }
})

vi.mock('@/api/mockWebSocket', () => ({
  mockWebSocket: {
    subscribe: wsMock.subscribe,
    unsubscribe: wsMock.unsubscribe
  }
}))

const RouterLinkStub = {
  template: '<a><slot /></a>',
  props: ['to']
}

const mountDashboard = () =>
  mount(ArtDecoDashboard, {
    global: {
      stubs: {
        'router-link': RouterLinkStub,
        ArtDecoChart: true,
        ArtDecoHeader: true,
        ArtDecoButton: true,
        ArtDecoIcon: true,
        ArtDecoBadge: true,
        ArtDecoSkeleton: true,
        ArtDecoCard: true,
        ArtDecoStatCard: true,
        ArtDecoCollapsible: true
      }
    }
  })

const flushMicrotasks = async () => {
  await Promise.resolve()
  await Promise.resolve()
}

describe('ArtDecoDashboard Logic Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    wsMock.reset()
  })

  it('loads dashboard data on mount', async () => {
    mountDashboard()
    await flushMicrotasks()

    expect(dashboardService.getMarketOverview).toHaveBeenCalled()
    expect(dashboardService.getFundFlow).toHaveBeenCalled()
    expect(dashboardService.getIndustryFlow).toHaveBeenCalled()
    expect(dashboardService.getStockFlowRanking).toHaveBeenCalled()
    expect(dashboardService.getActiveStrategies).toHaveBeenCalled()
    expect(marketService.getKline).toHaveBeenCalled()
  })

  it('subscribes to the explicit trend topic after trend data loads', async () => {
    mountDashboard()
    await flushMicrotasks()

    expect(mockWebSocket.subscribe).toHaveBeenCalledWith('market.trend.000001', expect.any(Function))
  })

  it('appends trend points from the mock trend stream payload', async () => {
    const wrapper = mountDashboard()
    await flushMicrotasks()

    const initialOption = (wrapper.vm as { marketTrendOption: { series?: Array<{ data?: number[] }> } | null }).marketTrendOption
    const initialLength = initialOption?.series?.[0]?.data?.length ?? 0
    wsMock.getTrendHandler()?.({
      topic: 'market.trend.000001',
      data: {
        timestamp: Date.now(),
        price: '3138.88'
      }
    })
    await flushMicrotasks()

    const nextOption = (wrapper.vm as { marketTrendOption: { series?: Array<{ data?: number[] }> } | null }).marketTrendOption
    const nextTrendData = nextOption?.series?.[0]?.data ?? []
    expect(nextTrendData.length).toBe(initialLength + 1)
    expect(nextTrendData.at(-1)).toBe(3138.88)
  })

  it('unsubscribes the dashboard trend listener on unmount', async () => {
    const wrapper = mountDashboard()
    await flushMicrotasks()

    wrapper.unmount()

    expect(mockWebSocket.unsubscribe).toHaveBeenCalledWith('market.trend.000001', expect.any(Function))
  })
})
