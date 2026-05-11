import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { computed, defineComponent } from 'vue'
import ArtDecoDashboard from '@/views/artdeco-pages/ArtDecoDashboard.vue'
import dashboardService from '@/api/services/dashboardService'
import { marketService } from '@/api/services/marketService'
import { mockWebSocket } from '@/api/mockWebSocket'
import { useHeaderSummary } from '@/composables/useHeaderSummary'
import { useArtDecoDashboard } from '@/views/artdeco-pages/composables/useArtDecoDashboard'

enableAutoUnmount(afterEach)

vi.mock('@/api/services/dashboardService', () => ({
  default: {
    getMarketOverview: vi.fn().mockResolvedValue({ data: [] }),
    getFundFlow: vi.fn().mockResolvedValue({ data: {} }),
    getIndustryFlow: vi.fn().mockResolvedValue({ data: [] }),
    getStockFlowRanking: vi.fn().mockResolvedValue({ data: [] }),
    getActiveStrategies: vi.fn().mockResolvedValue({ data: [] }),
    getPositionRisk: vi.fn().mockResolvedValue({ data: { totalPnL: 0 } }),
    getSystemHealth: vi.fn().mockResolvedValue({ data: [] }),
    getTechnicalIndicators: vi.fn().mockResolvedValue({ data: {} }),
    getTechnicalIndicatorsSafe: vi.fn().mockResolvedValue({ ok: true, data: {} })
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

const HeaderStub = defineComponent({
  props: {
    title: {
      type: String,
      default: '',
    },
    subtitle: {
      type: String,
      default: '',
    },
  },
  template: '<header class="header-stub"><h1>{{ title }}</h1><p>{{ subtitle }}</p></header>',
})

const DashboardStatCardStub = defineComponent({
  props: {
    label: {
      type: String,
      required: true,
    },
    value: {
      type: [String, Number],
      required: true,
    },
    change: {
      type: Number,
      default: 0,
    },
    showChange: {
      type: Boolean,
      default: true,
    },
    changePercent: {
      type: Boolean,
      default: true,
    },
    description: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    const displayChange = computed(() => {
      if (props.changePercent) {
        return `${props.change >= 0 ? '+' : ''}${props.change}%`
      }
      return `${props.change >= 0 ? '+' : ''}${props.change}`
    })

    return {
      displayChange,
    }
  },
  template: `
    <div class="stat-card-stub">
      <span class="stat-label">{{ label }}</span>
      <span class="stat-value">{{ value }}</span>
      <div v-if="change || showChange" class="artdeco-stat-change">{{ displayChange }}</div>
      <span v-if="description" class="stat-description">{{ description }}</span>
    </div>
  `,
})

const mountDashboard = () =>
  mount(ArtDecoDashboard, {
    global: {
      stubs: {
        'router-link': RouterLinkStub,
        ArtDecoChart: true,
        ArtDecoHeader: HeaderStub,
        ArtDecoButton: {
          emits: ['click'],
          template: '<button @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
        },
        ArtDecoIcon: true,
        ArtDecoBadge: true,
        ArtDecoSkeleton: true,
        ArtDecoCard: true,
        ArtDecoStatCard: true,
        ArtDecoCollapsible: {
          template: '<section class="collapsible-stub"><slot /></section>',
        }
      }
    }
  })

const mountDashboardWithRenderedCards = () =>
  mount(ArtDecoDashboard, {
    global: {
      stubs: {
        'router-link': RouterLinkStub,
        ArtDecoChart: true,
        ArtDecoHeader: HeaderStub,
        ArtDecoButton: true,
        ArtDecoIcon: true,
        ArtDecoBadge: true,
        ArtDecoSkeleton: true,
        ArtDecoCollapsible: {
          template: '<section class="collapsible-stub"><slot /></section>',
        },
        ArtDecoCard: {
          template: '<section><slot name="header" /><slot /></section>',
        },
        ArtDecoStatCard: DashboardStatCardStub,
      }
    }
  })

const DashboardFundFlowHarness = defineComponent({
  setup() {
    return useArtDecoDashboard()
  },
  template: `
    <div>
      <div v-if="dashboardAlerts.length > 0" class="dashboard-alerts">
        <span v-for="message in dashboardAlerts" :key="message">{{ message }}</span>
      </div>
      <div class="enhanced-fund-flow">
        <section v-if="error.fundFlow" class="error-message">{{ error.fundFlow }}</section>
        <section v-else class="summary-section">
          <span>沪股通净流入</span>
          <span>{{ marketData.fundFlow.hgt.amount }}亿</span>
        </section>
      </div>
      <button type="button" class="refresh-btn" @click="refreshData">刷新数据</button>
    </div>
  `,
})

const flushMicrotasks = async () => {
  await Promise.resolve()
  await Promise.resolve()
}

const settleDashboardHarness = async () => {
  await flushPromises()
  await flushPromises()
}

describe('ArtDecoDashboard Logic Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    wsMock.reset()
    vi.mocked(dashboardService.getMarketOverview).mockReset().mockResolvedValue({ request_id: 'dashboard-market-ok', data: [] })
    vi.mocked(dashboardService.getFundFlow).mockReset().mockResolvedValue({ request_id: 'dashboard-fund-flow-ok', data: {} })
    vi.mocked(dashboardService.getIndustryFlow).mockReset().mockResolvedValue({ request_id: 'dashboard-industry-ok', data: [] })
    vi.mocked(dashboardService.getStockFlowRanking).mockReset().mockResolvedValue({ request_id: 'dashboard-ranking-ok', data: [] })
    vi.mocked(dashboardService.getActiveStrategies).mockReset().mockResolvedValue({ request_id: 'dashboard-strategy-ok', data: [] })
    vi.mocked(dashboardService.getPositionRisk).mockReset().mockResolvedValue({ request_id: 'dashboard-risk-ok', data: { totalPnL: 0 } })
    vi.mocked(dashboardService.getSystemHealth).mockReset().mockResolvedValue({ request_id: 'dashboard-health-ok', data: [] })
    vi.mocked(dashboardService.getTechnicalIndicators).mockReset().mockResolvedValue({ request_id: 'dashboard-indicator-ok', data: {} })
    vi.mocked(dashboardService.getTechnicalIndicatorsSafe).mockReset().mockResolvedValue({ ok: true, data: {} })
    vi.mocked(marketService.getKline).mockReset().mockResolvedValue({ data: [] })
    const headerSummary = useHeaderSummary()
    headerSummary.update({
      marketStatus: '',
      activeStrategiesCount: null,
      todayPnLValue: '¥0.00',
      currentTime: '',
      refreshing: false,
    })
    headerSummary.setRefreshFn(async () => {})
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

  it('uses a task-recognizable dashboard title while retaining the QUANTIX brand cue', async () => {
    const wrapper = mountDashboard()
    await flushMicrotasks()

    expect(wrapper.find('.header-stub').text()).toContain('量化驾驶舱')
    expect(wrapper.find('.header-stub').text()).toContain('QUANTIX')
  })

  it('subscribes to the explicit trend topic after trend data loads', async () => {
    mountDashboard()
    await flushMicrotasks()

    expect(mockWebSocket.subscribe).toHaveBeenCalledWith('market.trend.000001', expect.any(Function))
  })

  it('appends trend points from the mock trend stream payload', async () => {
    const wrapper = mountDashboardWithRenderedCards()
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

  it('syncs dashboard summary data into the shared header store', async () => {
    mountDashboard()
    await flushMicrotasks()

    const headerSummary = useHeaderSummary()

    expect(headerSummary.marketStatus.value).toBe('市场震荡')
    expect(headerSummary.activeStrategiesCount.value).toBe(0)
    expect(headerSummary.todayPnLValue.value).toBe('¥0')
    expect(headerSummary.currentTime.value).toBeTruthy()
    expect(headerSummary.refreshing.value).toBe(false)
  })

  it('keeps the shared header refresh action bound after the dashboard bootstrap reset path runs', async () => {
    mountDashboard()
    await flushMicrotasks()

    expect(dashboardService.getFundFlow).toHaveBeenCalledTimes(1)

    const headerSummary = useHeaderSummary()
    await headerSummary.refresh()
    await flushMicrotasks()

    expect(dashboardService.getFundFlow).toHaveBeenCalledTimes(2)
    expect(dashboardService.getMarketOverview).toHaveBeenCalledTimes(2)
    expect(dashboardService.getIndustryFlow).toHaveBeenCalledTimes(2)
  })

  it('reports mixed aggregate provenance when a core dashboard slice resolves a unified error envelope after other core slices resolve', async () => {
    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      success: false,
      message: 'industry unavailable',
      request_id: 'dashboard-industry-fail',
      data: null,
    } as never)

    const wrapper = mountDashboard()
    await flushMicrotasks()

    expect(wrapper.find('.request-meta-bar').text()).toContain('DATA: MIXED')
    expect(wrapper.find('.request-meta-bar').text()).toContain('SYNC: DEGRADED')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('DATA: REAL')
    expect(wrapper.find('.dashboard-alerts').text()).toContain('行业热度数据暂不可用')
  })

  it('reports mixed aggregate provenance when the fund-flow slice resolves a unified error envelope after other core slices resolve', async () => {
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      success: false,
      message: 'fund flow unavailable',
      request_id: 'dashboard-fund-flow-fail',
      data: null,
    } as never)

    const wrapper = mountDashboard()
    await flushMicrotasks()

    expect(wrapper.find('.request-meta-bar').text()).toContain('DATA: MIXED')
    expect(wrapper.find('.request-meta-bar').text()).toContain('SYNC: DEGRADED')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('DATA: REAL')
    expect(wrapper.find('.dashboard-alerts').text()).toContain('资金流向数据暂不可用')
  })

  it('reports pending aggregate provenance while every core dashboard slice is still unresolved', async () => {
    const never = new Promise(() => {})
    vi.mocked(dashboardService.getMarketOverview).mockReturnValueOnce(never as Promise<{ data: [] }>)
    vi.mocked(dashboardService.getFundFlow).mockReturnValueOnce(never as Promise<{ data: {} }>)
    vi.mocked(dashboardService.getIndustryFlow).mockReturnValueOnce(never as Promise<{ data: [] }>)

    const wrapper = mountDashboard()
    await flushMicrotasks()

    expect(wrapper.find('.request-meta-bar').text()).toContain('DATA: PENDING')
    expect(wrapper.find('.request-meta-bar').text()).toContain('SYNC: PENDING')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('DATA: REAL')
    expect(wrapper.find('.dashboard-alerts').exists()).toBe(false)
  })

  it('keeps dashboard request meta bound to the verified core-slice trace instead of later auxiliary slice requests', async () => {
    vi.mocked(dashboardService.getMarketOverview).mockResolvedValueOnce({
      request_id: 'dashboard-market-core',
      process_time: '11',
      data: [],
    } as never)
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      request_id: 'dashboard-fund-flow-core',
      process_time: '22',
      data: {},
    } as never)
    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      request_id: 'dashboard-industry-core',
      process_time: '33',
      data: [],
    } as never)
    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      request_id: 'dashboard-ranking-aux',
      process_time: '44',
      data: [],
    } as never)
    vi.mocked(dashboardService.getActiveStrategies).mockResolvedValueOnce({
      request_id: 'dashboard-strategy-aux',
      process_time: '55',
      data: [],
    } as never)
    vi.mocked(dashboardService.getPositionRisk).mockResolvedValueOnce({
      request_id: 'dashboard-risk-aux',
      process_time: '66',
      data: { totalPnL: 0 },
    } as never)
    vi.mocked(dashboardService.getSystemHealth).mockResolvedValueOnce({
      request_id: 'dashboard-health-aux',
      process_time: '77',
      data: [],
    } as never)
    vi.mocked(dashboardService.getTechnicalIndicators).mockResolvedValueOnce({
      request_id: 'dashboard-indicator-aux',
      process_time: '88',
      data: {},
    } as never)

    const wrapper = mountDashboard()
    await flushMicrotasks()

    expect(wrapper.find('.request-meta-bar').text()).toContain('REQ: dashboard-industry-core')
    expect(wrapper.find('.request-meta-bar').text()).toContain('TIME: 33ms')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-ranking-aux')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-strategy-aux')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-risk-aux')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-health-aux')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-indicator-aux')
  })

  it('does not leak failed or auxiliary request ids before any core dashboard slice has produced a verified snapshot', async () => {
    vi.mocked(dashboardService.getMarketOverview).mockResolvedValueOnce({
      success: false,
      message: 'market unavailable',
      request_id: 'dashboard-market-first-fail',
      process_time: '91',
      data: null,
    } as never)
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      success: false,
      message: 'fund flow unavailable',
      request_id: 'dashboard-fund-flow-first-fail',
      process_time: '92',
      data: null,
    } as never)
    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      success: false,
      message: 'industry unavailable',
      request_id: 'dashboard-industry-first-fail',
      process_time: '93',
      data: null,
    } as never)
    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      request_id: 'dashboard-ranking-aux',
      process_time: '44',
      data: [],
    } as never)
    vi.mocked(dashboardService.getActiveStrategies).mockResolvedValueOnce({
      request_id: 'dashboard-strategy-aux',
      process_time: '55',
      data: [],
    } as never)
    vi.mocked(dashboardService.getPositionRisk).mockResolvedValueOnce({
      request_id: 'dashboard-risk-aux',
      process_time: '66',
      data: { totalPnL: 0 },
    } as never)
    vi.mocked(dashboardService.getSystemHealth).mockResolvedValueOnce({
      request_id: 'dashboard-health-aux',
      process_time: '77',
      data: [],
    } as never)
    vi.mocked(dashboardService.getTechnicalIndicators).mockResolvedValueOnce({
      request_id: 'dashboard-indicator-aux',
      process_time: '88',
      data: {},
    } as never)

    const wrapper = mountDashboard()
    await flushMicrotasks()

    expect(wrapper.find('.request-meta-bar').text()).toContain('DATA: UNAVAILABLE')
    expect(wrapper.find('.request-meta-bar').text()).toContain('SYNC: UNAVAILABLE')
    expect(wrapper.find('.request-meta-bar').text()).toContain('REQ: N/A')
    expect(wrapper.find('.request-meta-bar').text()).toContain('TIME: --')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-market-first-fail')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-fund-flow-first-fail')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-industry-first-fail')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-ranking-aux')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-indicator-aux')
  })

  it('keeps the last verified core request trace when a later refresh fails before any new core snapshot is verified', async () => {
    vi.mocked(dashboardService.getMarketOverview).mockResolvedValueOnce({
      request_id: 'dashboard-market-core',
      process_time: '11',
      data: [],
    } as never)
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      request_id: 'dashboard-fund-flow-core',
      process_time: '22',
      data: {},
    } as never)
    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      request_id: 'dashboard-industry-core',
      process_time: '33',
      data: [],
    } as never)

    const wrapper = mountDashboard()
    await flushMicrotasks()

    vi.mocked(dashboardService.getMarketOverview).mockResolvedValueOnce({
      success: false,
      message: 'market refresh unavailable',
      request_id: 'dashboard-market-refresh-fail',
      process_time: '111',
      data: null,
    } as never)
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      success: false,
      message: 'fund flow refresh unavailable',
      request_id: 'dashboard-fund-flow-refresh-fail',
      process_time: '122',
      data: null,
    } as never)
    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      success: false,
      message: 'industry refresh unavailable',
      request_id: 'dashboard-industry-refresh-fail',
      process_time: '133',
      data: null,
    } as never)
    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      request_id: 'dashboard-ranking-refresh-aux',
      process_time: '144',
      data: [],
    } as never)
    vi.mocked(dashboardService.getActiveStrategies).mockResolvedValueOnce({
      request_id: 'dashboard-strategy-refresh-aux',
      process_time: '155',
      data: [],
    } as never)
    vi.mocked(dashboardService.getPositionRisk).mockResolvedValueOnce({
      request_id: 'dashboard-risk-refresh-aux',
      process_time: '166',
      data: { totalPnL: 0 },
    } as never)
    vi.mocked(dashboardService.getSystemHealth).mockResolvedValueOnce({
      request_id: 'dashboard-health-refresh-aux',
      process_time: '177',
      data: [],
    } as never)
    vi.mocked(dashboardService.getTechnicalIndicators).mockResolvedValueOnce({
      request_id: 'dashboard-indicator-refresh-aux',
      process_time: '188',
      data: {},
    } as never)

    await useHeaderSummary().refresh()
    await flushMicrotasks()

    expect(wrapper.find('.request-meta-bar').text()).toContain('REQ: dashboard-industry-core')
    expect(wrapper.find('.request-meta-bar').text()).toContain('TIME: 33ms')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-market-refresh-fail')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-fund-flow-refresh-fail')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-industry-refresh-fail')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-ranking-refresh-aux')
    expect(wrapper.find('.request-meta-bar').text()).not.toContain('dashboard-indicator-refresh-aux')
  })

  it('keeps the last verified fund-flow slice visible when a later fund-flow refresh fails', async () => {
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      request_id: 'dashboard-fund-flow-success',
      process_time: '22',
      data: {
        hgt: { amount: 18.5, change: 0.82 },
        sgt: { amount: 9.3, change: 0.45 },
        northTotal: { amount: 27.8, monthly: 86.1 },
        mainForce: { amount: 4.2, percentage: 13.6 },
      },
    } as never)

    const wrapper = mount(DashboardFundFlowHarness)
    await settleDashboardHarness()

    expect(wrapper.find('.enhanced-fund-flow .summary-section').exists()).toBe(true)
    expect(wrapper.find('.enhanced-fund-flow').text()).toContain('沪股通净流入')
    expect(wrapper.find('.enhanced-fund-flow').text()).toContain('18.5亿')

    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      success: false,
      message: 'fund flow refresh unavailable',
      request_id: 'dashboard-fund-flow-refresh-fail',
      process_time: '122',
      data: null,
    } as never)

    await wrapper.get('.refresh-btn').trigger('click')
    await settleDashboardHarness()

    expect(dashboardService.getFundFlow).toHaveBeenCalledTimes(2)
    expect(wrapper.find('.dashboard-alerts').text()).toContain('资金流向数据暂不可用')
    expect((wrapper.vm as { dashboardAlertItems: Array<{ label: string; action: string }> }).dashboardAlertItems[0].label).toBe('DEGRADED')
    expect((wrapper.vm as { dashboardAlertItems: Array<{ label: string; action: string }> }).dashboardAlertItems[0].action).toContain('上次成功同步')
    expect(wrapper.find('.enhanced-fund-flow .summary-section').exists()).toBe(true)
    expect(wrapper.find('.enhanced-fund-flow').text()).toContain('沪股通净流入')
    expect(wrapper.find('.enhanced-fund-flow').text()).toContain('18.5亿')
    expect(wrapper.find('.enhanced-fund-flow .error-message').exists()).toBe(false)
  })

  it('keeps the last verified industry slice visible when a later industry refresh fails', async () => {
    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      request_id: 'dashboard-industry-success',
      process_time: '33',
      data: [
        { name: '半导体', change: 3.28, amount: 1280000000 },
        { name: '算力', change: 2.16, amount: 860000000 },
      ],
    } as never)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.request-meta-bar').text()).toContain('DATA: REAL')
    expect(wrapper.find('.request-meta-bar').text()).toContain('SYNC: READY')
    expect(wrapper.find('.market-status-card').text()).toContain('涨跌家数')
    expect(wrapper.find('.market-status-card').text()).toContain('2↑/0↓')
    expect(wrapper.find('.heat-map-card .chart-state-note').exists()).toBe(false)
    expect(wrapper.find('.sector-radar-card .chart-state-note').exists()).toBe(false)

    vi.mocked(dashboardService.getIndustryFlow).mockResolvedValueOnce({
      success: false,
      message: 'industry refresh unavailable',
      request_id: 'dashboard-industry-refresh-fail',
      process_time: '133',
      data: null,
    } as never)

    await useHeaderSummary().refresh()
    await settleDashboardHarness()

    expect(wrapper.find('.request-meta-bar').text()).toContain('DATA: MIXED')
    expect(wrapper.find('.request-meta-bar').text()).toContain('SYNC: DEGRADED')
    expect(wrapper.find('.dashboard-alerts').text()).toContain('行业热度数据暂不可用')
    expect(wrapper.find('.dashboard-alerts').text()).toContain('DEGRADED')
    expect(wrapper.find('.dashboard-alerts').text()).toContain('上次成功同步的行业热度')
    expect(wrapper.find('.market-status-card').text()).toContain('涨跌家数')
    expect(wrapper.find('.market-status-card').text()).toContain('2↑/0↓')
    expect(wrapper.find('.heat-map-card .chart-state-note').exists()).toBe(false)
    expect(wrapper.find('.sector-radar-card .chart-state-note').exists()).toBe(false)
  })

  it('keeps the last verified capital-flow slice visible when a later ranking refresh fails', async () => {
    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      request_id: 'dashboard-ranking-success',
      process_time: '44',
      data: [
        { name: '贵州茅台', code: '600519', amount: 9.8, change: 1.2 },
        { name: '宁德时代', code: '300750', amount: -4.2, change: -0.8 },
      ],
    } as never)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.capital-flow-card').text()).toContain('贵州茅台')
    expect(wrapper.find('.capital-flow-card').text()).toContain('宁德时代')
    expect((wrapper.vm as { capitalFlowHeatmapOption: unknown }).capitalFlowHeatmapOption).not.toBeNull()

    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      success: false,
      message: 'stock flow ranking unavailable',
      request_id: 'dashboard-ranking-refresh-fail',
      process_time: '144',
      data: null,
    } as never)

    await useHeaderSummary().refresh()
    await settleDashboardHarness()

    expect(wrapper.find('.capital-flow-card').text()).toContain('资金流向持续排名暂不可用')
    expect(wrapper.find('.capital-flow-card').text()).toContain('贵州茅台')
    expect(wrapper.find('.capital-flow-card').text()).toContain('宁德时代')
    expect((wrapper.vm as { capitalFlowHeatmapOption: unknown }).capitalFlowHeatmapOption).not.toBeNull()
  })

  it('does not leak the last verified capital-flow rows into a different tab while that tab is still on its first unresolved load', async () => {
    vi.mocked(dashboardService.getStockFlowRanking)
      .mockResolvedValueOnce({
        request_id: 'dashboard-ranking-1day-success',
        process_time: '44',
        data: [
          { name: '贵州茅台', code: '600519', amount: 9.8, change: 1.2 },
          { name: '宁德时代', code: '300750', amount: -4.2, change: -0.8 },
        ],
      } as never)
      .mockReturnValueOnce(new Promise(() => {}) as Promise<never>)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.capital-flow-card').text()).toContain('贵州茅台')
    expect(wrapper.find('.capital-flow-card').text()).toContain('宁德时代')

    const flowTabs = wrapper.findAll('.capital-flow-card .flow-tab')
    await flowTabs[1].trigger('click')
    await flushMicrotasks()

    expect(flowTabs[1].classes()).toContain('active')
    expect(wrapper.find('.capital-flow-card').text()).not.toContain('贵州茅台')
    expect(wrapper.find('.capital-flow-card').text()).not.toContain('宁德时代')
  })

  it('keeps the last verified capital-flow slice visible when the shared big-deal refresh breaks both fund-flow and ranking fetches', async () => {
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      request_id: 'dashboard-fund-flow-success',
      process_time: '22',
      data: {
        hgt: { amount: 18.5, change: 0.82 },
        sgt: { amount: 9.3, change: 0.45 },
        northTotal: { amount: 27.8, monthly: 86.1 },
        mainForce: { amount: 4.2, percentage: 13.6 },
      },
    } as never)
    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      request_id: 'dashboard-ranking-success',
      process_time: '44',
      data: [
        { name: '贵州茅台', code: '600519', amount: 9.8, change: 1.2 },
        { name: '宁德时代', code: '300750', amount: -4.2, change: -0.8 },
      ],
    } as never)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      success: false,
      message: 'fund flow refresh unavailable',
      request_id: 'dashboard-fund-flow-refresh-fail',
      process_time: '122',
      data: null,
    } as never)
    vi.mocked(dashboardService.getStockFlowRanking).mockResolvedValueOnce({
      success: false,
      message: 'stock flow ranking unavailable',
      request_id: 'dashboard-ranking-refresh-fail',
      process_time: '144',
      data: null,
    } as never)

    await useHeaderSummary().refresh()
    await settleDashboardHarness()

    expect(wrapper.find('.dashboard-alerts').text()).toContain('资金流向数据暂不可用')
    expect(wrapper.find('.capital-flow-card').text()).toContain('资金流向持续排名暂不可用')
    expect(wrapper.find('.capital-flow-card').text()).toContain('贵州茅台')
    expect(wrapper.find('.capital-flow-card').text()).toContain('宁德时代')
    expect((wrapper.vm as { capitalFlowHeatmapOption: unknown }).capitalFlowHeatmapOption).not.toBeNull()
  })

  it('keeps the last verified trend slice visible when a later trend refresh fails', async () => {
    vi.mocked(marketService.getKline)
      .mockResolvedValueOnce({
        data: [
          { date: '2026-05-01', close: 3201.12 },
          { date: '2026-05-02', close: 3214.56 },
          { date: '2026-05-03', close: 3228.44 },
        ],
      } as never)
      .mockResolvedValueOnce({
        success: false,
        request_id: 'dashboard-kline-refresh-fail',
        message: 'kline refresh unavailable',
        data: null,
      } as never)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect((wrapper.vm as { marketTrendOption: { series?: Array<{ data?: number[] }> } | null }).marketTrendOption).not.toBeNull()
    expect(wrapper.find('.market-indicators .chart-section .integration-note').exists()).toBe(false)

    await useHeaderSummary().refresh()
    await settleDashboardHarness()

    expect((wrapper.vm as { marketTrendOption: { series?: Array<{ data?: number[] }> } | null }).marketTrendOption).not.toBeNull()
    expect(wrapper.find('.market-indicators .chart-section .integration-note').text()).toContain('分时趋势暂不可用，当前仍显示上次成功同步的分时趋势快照。')
    expect(wrapper.find('.market-indicators .chart-section').text()).not.toContain('当前暂无已验证分时趋势快照。')
  })

  it('reports explicit unavailable truth when the technical-indicator slice fails before any verified snapshot exists', async () => {
    vi.mocked(dashboardService.getTechnicalIndicatorsSafe).mockResolvedValueOnce({
      ok: false,
      data: {},
      error: 'indicator refresh unavailable',
    })

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.indicators-section').text()).toContain('技术指标暂不可用')
    expect(wrapper.find('.indicators-section').text()).toContain('当前暂无已验证指标快照')
    expect(wrapper.find('.indicators-section').text()).not.toContain('技术指标真实接口待接入')
  })

  it('keeps the last verified technical-indicator slice visible when a later indicator refresh fails', async () => {
    vi.mocked(dashboardService.getTechnicalIndicatorsSafe).mockResolvedValueOnce({
      ok: true,
      data: {
        '000001.SH': [
          { name: 'RSI', value: '61.2', trend: 'rise', signal: '偏强' },
          { name: 'MACD', value: '0.82', trend: 'rise', signal: '金叉' },
        ],
      },
    })

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.indicators-section').text()).toContain('RSI')
    expect(wrapper.find('.indicators-section').text()).toContain('61.2')

    vi.mocked(dashboardService.getTechnicalIndicatorsSafe).mockResolvedValueOnce({
      ok: false,
      data: {},
      error: 'indicator refresh unavailable',
    })

    await useHeaderSummary().refresh()
    await settleDashboardHarness()

    expect(wrapper.find('.indicators-section').text()).toContain('技术指标暂不可用')
    expect(wrapper.find('.indicators-section').text()).toContain('当前仍显示上次成功同步的技术指标快照')
    expect(wrapper.find('.indicators-section').text()).toContain('RSI')
    expect(wrapper.find('.indicators-section').text()).toContain('61.2')
  })

  it('reports explicit unavailable truth when the monitoring slice fails before any verified snapshot exists', async () => {
    vi.mocked(dashboardService.getSystemHealth).mockRejectedValueOnce(new Error('system health unavailable'))

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.monitoring-section').text()).toContain('系统监控暂不可用')
    expect(wrapper.find('.monitoring-section').text()).toContain('当前暂无已验证监控快照')
    expect(wrapper.find('.monitoring-section').text()).not.toContain('系统监控真实接口待接入')
  })

  it('keeps the last verified monitoring slice visible when a later monitoring refresh fails', async () => {
    vi.mocked(dashboardService.getSystemHealth).mockResolvedValueOnce({
      request_id: 'dashboard-health-success',
      process_time: '77',
      data: [
        { label: '服务状态', value: 'HEALTHY', status: 'good' },
        { label: '服务名称', value: 'mystocks-backend', status: 'good' },
        { label: '版本', value: '2.0.0', status: 'good' },
      ],
    } as never)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    expect(wrapper.find('.monitoring-section').text()).toContain('服务状态')
    expect(wrapper.find('.monitoring-section').text()).toContain('HEALTHY')

    vi.mocked(dashboardService.getSystemHealth).mockRejectedValueOnce(new Error('system health unavailable'))

    await useHeaderSummary().refresh()
    await settleDashboardHarness()

    expect(wrapper.find('.monitoring-section').text()).toContain('系统监控暂不可用')
    expect(wrapper.find('.monitoring-section').text()).toContain('当前仍显示上次成功同步的监控快照')
    expect(wrapper.find('.monitoring-section').text()).toContain('服务状态')
    expect(wrapper.find('.monitoring-section').text()).toContain('HEALTHY')
  })

  it('does not render default change chrome for description-only fund-flow summary cards', async () => {
    vi.mocked(dashboardService.getFundFlow).mockResolvedValueOnce({
      request_id: 'dashboard-fund-flow-summary-success',
      process_time: '22',
      data: {
        hgt: { amount: 18.5, change: 1.2 },
        sgt: { amount: 9.3, change: -0.4 },
        northTotal: { amount: 27.8, monthly: 136.2 },
        mainForce: { amount: 12.4, percentage: 61.5 },
      },
    } as never)

    const wrapper = mountDashboardWithRenderedCards()
    await settleDashboardHarness()

    const fundFlowSection = wrapper.find('.enhanced-fund-flow')
    expect(fundFlowSection.text()).toContain('北向资金总额')
    expect(fundFlowSection.text()).toContain('主力净流入')
    expect(fundFlowSection.findAll('.artdeco-stat-change')).toHaveLength(2)
    expect(fundFlowSection.text()).toContain('+1.2')
    expect(fundFlowSection.text()).toContain('-0.4')
    expect(fundFlowSection.text()).not.toContain('+0%')
  })
})
