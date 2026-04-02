import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { getStockDetailMock, getKlineMock, successMock, errorMock } = vi.hoisted(() => ({
  getStockDetailMock: vi.fn(),
  getKlineMock: vi.fn(),
  successMock: vi.fn(),
  errorMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { symbol: '600519' },
    query: {},
  }),
}))

vi.mock('@/api', () => ({
  dataApi: {
    getStockDetail: getStockDetailMock,
    getKline: getKlineMock,
  },
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual<typeof import('element-plus')>('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: successMock,
      error: errorMock,
      info: vi.fn(),
      warning: vi.fn(),
    },
  }
})

import StockDetail from '@/views/StockDetail.vue'

describe('StockDetail trading summary', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-04-02T00:00:00Z'))
    vi.clearAllMocks()

    getStockDetailMock.mockResolvedValue({
      success: true,
      data: {
        symbol: '600519',
        name: '贵州茅台',
        price: '1800.00',
        change: '10.00',
        change_pct: '0.56',
        market: 'SH',
        industry: '白酒',
        concepts: ['消费'],
        area: '贵州',
        list_date: '2001-08-27',
      },
    })

    getKlineMock.mockResolvedValue({
      success: true,
      data: [
        { date: '2026-03-01', open: 9, high: 11, low: 8, close: 10, volume: 100, amount: 1000 },
        { date: '2026-03-15', open: 10, high: 13, low: 10, close: 12, volume: 200, amount: 2400 },
        { date: '2026-04-01', open: 12, high: 12, low: 8, close: 9, volume: 150, amount: 1350 },
      ],
    })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('derives trading summary metrics from kline data instead of random fallback data', async () => {
    const wrapper = mount(StockDetail as never, {
      global: {
        stubs: {
          ProKLineChart: true,
          'el-card': { template: '<div><slot name="header" /><slot /></div>' },
          'el-button': { template: '<button><slot /></button>' },
          'el-input': { template: '<input />' },
          'el-icon': { template: '<i><slot /></i>' },
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
          'el-descriptions': { template: '<div><slot /></div>' },
          'el-descriptions-item': { template: '<div><slot /></div>' },
        },
        directives: {
          loading: { mounted() {}, updated() {} },
        },
      },
    })

    await flushPromises()

    expect(getKlineMock).toHaveBeenCalledWith({
      stock_code: '600519',
      period: 'daily',
      adjust: 'qfq',
      start_date: '2026-03-03',
      end_date: '2026-04-02',
    })

    const summaryText = wrapper.find('.summary-content').text()
    expect(summaryText).toContain('-1')
    expect(summaryText).toContain('-10')
    expect(summaryText).toContain('13')
    expect(summaryText).toContain('8')
    expect(summaryText).toContain('450')
    expect(summaryText).toContain('4750')
    expect(summaryText).toContain('50')
    expect(summaryText).toContain('-25')
  })
})
