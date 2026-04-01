import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getKLineDataMock,
  initMock,
  disposeMock,
  applyNewDataMock,
  setStylesMock,
  applySelectedIndicatorsMock,
  onMountedMock,
  onUnmountedMock,
  watchMock,
} = vi.hoisted(() => ({
  getKLineDataMock: vi.fn(),
  initMock: vi.fn(),
  disposeMock: vi.fn(),
  applyNewDataMock: vi.fn(),
  setStylesMock: vi.fn(),
  applySelectedIndicatorsMock: vi.fn(),
  onMountedMock: vi.fn(),
  onUnmountedMock: vi.fn(),
  watchMock: vi.fn(),
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: onMountedMock,
    onUnmounted: onUnmountedMock,
    watch: watchMock,
  }
})

vi.mock('@/api/market', () => ({
  marketApi: {
    getKLineData: getKLineDataMock,
  },
}))

vi.mock('klinecharts', () => ({
  init: initMock.mockImplementation(() => ({
    applyNewData: applyNewDataMock,
    setStyles: setStylesMock,
    getTimeScaleVisibleRange: vi.fn(() => ({ from: 0, to: 100 })),
    getVisibleRange: vi.fn(() => ({ from: 0, to: 100 })),
  })),
  dispose: disposeMock,
}))

vi.mock('@/components/market/composables/useProKLineChart.chart-config.ts', () => ({
  applyChartContainerHeight: vi.fn(),
  createProKLineChartStyleConfig: vi.fn(() => ({})),
}))

vi.mock('@/components/market/composables/useProKLineChart.indicators.ts', () => ({
  applyKDJIndicator: vi.fn(),
  applyMACDIndicator: vi.fn(),
  applyMAIndicator: vi.fn(),
  applyRSIIndicator: vi.fn(),
  applySelectedIndicators: applySelectedIndicatorsMock,
  applyVolumeIndicator: vi.fn(),
}))

vi.mock('@/components/market/composables/useProKLineChart.price-limits.ts', () => ({
  applyPriceLimitOverlay: vi.fn(),
  calculatePriceLimitMarkers: vi.fn(() => []),
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    warning: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}))

import { useProKLineChart } from '@/components/market/composables/useProKLineChart'

describe('useProKLineChart market data adapter', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(globalThis as Record<string, unknown>).defineProps = () => ({
      symbol: '000001.SZ',
      forwardAdjusted: true,
    })
    ;(globalThis as Record<string, unknown>).withDefaults = (props: Record<string, unknown>, defaults: Record<string, unknown>) => ({
      ...defaults,
      ...props,
    })
    ;(globalThis as Record<string, unknown>).defineEmits = () => vi.fn()

    getKLineDataMock.mockResolvedValue({
      categoryData: ['2026-04-01T09:30:00Z', '2026-04-01T09:31:00Z'],
      values: [
        [10, 11, 9, 12],
        [11, 10.5, 10, 11.5],
      ],
      volumes: [1000, 1200],
    })
  })

  afterEach(() => {
    delete (globalThis as Record<string, unknown>).defineProps
    delete (globalThis as Record<string, unknown>).withDefaults
    delete (globalThis as Record<string, unknown>).defineEmits
  })

  it('converts KLineChartData payloads into klinecharts data with qfq adjustment', async () => {
    const chart = useProKLineChart()
    chart.chartContainer.value = document.createElement('div')
    chart.initChart()

    await chart.loadHistoricalData()

    expect(getKLineDataMock).toHaveBeenCalledWith(
      expect.objectContaining({
        symbol: '000001.SZ',
        interval: '1d',
        limit: 1000,
        adjust: 'qfq',
      }),
    )
    expect(applyNewDataMock).toHaveBeenCalledWith([
      {
        timestamp: Date.parse('2026-04-01T09:30:00Z'),
        open: 10,
        high: 12,
        low: 9,
        close: 11,
        volume: 1000,
      },
      {
        timestamp: Date.parse('2026-04-01T09:31:00Z'),
        open: 11,
        high: 11.5,
        low: 10,
        close: 10.5,
        volume: 1200,
      },
    ])
  })
})
