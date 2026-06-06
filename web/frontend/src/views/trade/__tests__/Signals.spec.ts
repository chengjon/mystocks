import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  refreshMock,
  loadingMock,
  errorMock,
  lastRequestIdMock,
  lastProcessTimeMock,
} = vi.hoisted(() => ({
  refreshMock: vi.fn(),
  loadingMock: { value: false },
  errorMock: { value: null as string | null },
  lastRequestIdMock: { value: 'req-trade-signals' },
  lastProcessTimeMock: { value: '25.2' },
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: () => ({
      loading: loadingMock,
      error: errorMock,
      lastRequestId: lastRequestIdMock,
      lastProcessTime: lastProcessTimeMock,
    }),
  }
})

vi.mock('@/stores/apiStores', () => ({
  useTradingSignalsStore: () => ({
    refresh: refreshMock,
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['disabled'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<section><h3 v-if="title">{{ title }}</h3><slot /></section>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<div><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></div>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
  }
})

import TradeSignalsPage from '../Signals.vue'

function mountSignalsPage() {
  return mount(TradeSignalsPage as never, {
    global: {
      stubs: {
      },
      directives: {
        loading: {},
      },
    },
  })
}

describe('TradeSignals routed signal truth', () => {
  beforeEach(() => {
    refreshMock.mockReset().mockResolvedValue({
      data: [
        {
          signal_id: 'sig-buy-001',
          symbol: '600519',
          name: '贵州茅台',
          type: 'BUY',
          price: 1688.2,
          time: '09:35:12',
          strategy: 'Momentum Alpha',
        },
        {
          symbol: '300750',
          name: '宁德时代',
          type: 'SELL',
          price: 212.6,
          time: '10:02:45',
          strategy: 'Breakdown Guard',
        },
        {
          symbol: '002594',
          name: '比亚迪',
          type: 'HOLD',
          price: 258.3,
          time: '10:18:08',
          strategy: 'Momentum Alpha',
        },
      ],
    })
    loadingMock.value = false
    errorMock.value = null
    lastRequestIdMock.value = 'req-trade-signals'
    lastProcessTimeMock.value = '25.2'
  })

  it('does not fabricate executable signal detail or execution analytics when the live payload only returns current signals', async () => {
    const wrapper = mountSignalsPage()

    await flushPromises()

    expect(refreshMock).toHaveBeenCalledWith({ limit: 20 })
    expect(wrapper.text()).toContain('信号在线 / 分析待接入')
    expect(wrapper.text()).toContain('信号准确率未校验')
    expect(wrapper.text()).toContain('信号响应时间25.20ms')
    expect(wrapper.text()).toContain('信号覆盖率待接入')
    expect(wrapper.text()).toContain('信号质量评分待接入')
    expect(wrapper.text()).toContain('当前实时信号流未返回执行结果统计，质量分析与历史追踪待接入。')
    expect(wrapper.text()).toContain('暂无已验证执行历史。')
    expect(wrapper.text()).toContain('策略来源：Momentum Alpha')
    expect(wrapper.text()).toContain('策略来源：Breakdown Guard')
    expect(wrapper.text()).toContain('观望')
    expect(wrapper.text()).toContain('观察')
    expect(wrapper.text()).toContain('未校验')
    expect(wrapper.text()).not.toContain('88%')
    expect(wrapper.text()).not.toContain('76%')
    expect(wrapper.text()).not.toContain('Momentum Alpha 信号触发')

    const holdRow = wrapper.findAll('.artdeco-trading-signals__row')[2]
    expect(holdRow?.text()).toContain('观望')
    expect(holdRow?.text()).toContain('观察')
    expect(holdRow?.find('button').attributes('disabled')).toBeDefined()
  })

  it('does not render trade-signal tally or pending-analysis cards as faux delta metrics with fabricated decimal precision', async () => {
    const wrapper = mountSignalsPage()

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['3', '1', '1', '未校验'])
    expect(wrapper.findAll('.signal-overview-grid .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.text()).not.toContain('+0%')
    expect(wrapper.text()).not.toContain('3.00')
    expect(wrapper.text()).not.toContain('1.00')
    expect(wrapper.text()).not.toContain('0.00')
  })

  it('does not present trade signals as REAL while the first signal payload is still unresolved', async () => {
    loadingMock.value = true
    refreshMock.mockReset().mockImplementation(() => new Promise(() => {}))

    const wrapper = mountSignalsPage()

    await Promise.resolve()

    expect(wrapper.get('.hero-meta').text()).toContain('COUNT: --')
    expect(wrapper.get('.hero-meta').text()).toContain('DATA: PENDING')
    expect(wrapper.get('.hero-meta').text()).not.toContain('DATA: REAL')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('交易信号同步中...')
  })

  it('does not present failed first-load trade signals as REAL or faux zero counts before any verified snapshot exists', async () => {
    errorMock.value = null
    refreshMock.mockResolvedValue({
      success: false,
      message: 'trade signals unavailable',
      data: null,
    })

    const wrapper = mountSignalsPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('COUNT: --')
    expect(wrapper.get('.hero-meta').text()).toContain('DATA: UNAVAILABLE')
    expect(wrapper.get('.hero-meta').text()).not.toContain('DATA: REAL')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('trade signals unavailable')
    expect(wrapper.text()).not.toContain('COUNT: 0')
  })

  it('keeps the last verified trade signals and request provenance when a manual refresh fails', async () => {
    refreshMock.mockReset()
    refreshMock
      .mockImplementationOnce(async () => {
        lastRequestIdMock.value = 'req-trade-signals-success'
        lastProcessTimeMock.value = '25.2'
        return {
          data: [
            {
              signal_id: 'sig-buy-001',
              symbol: '600519',
              name: '贵州茅台',
              type: 'BUY',
              price: 1688.2,
              time: '09:35:12',
              strategy: 'Momentum Alpha',
            },
            {
              symbol: '300750',
              name: '宁德时代',
              type: 'SELL',
              price: 212.6,
              time: '10:02:45',
              strategy: 'Breakdown Guard',
            },
          ],
        }
      })
      .mockImplementationOnce(async () => {
        lastRequestIdMock.value = 'req-trade-signals-refresh-fail'
        lastProcessTimeMock.value = '44.6'
        return {
          success: false,
          message: 'trade signals refresh unavailable',
          data: null,
        }
      })

    const wrapper = mountSignalsPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-trade-signals-success')
    expect(wrapper.findAll('.artdeco-trading-signals__row')).toHaveLength(2)

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('COUNT: 2')
    expect(wrapper.get('.hero-meta').text()).toContain('DATA: REAL')
    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-trade-signals-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('REQ_ID: req-trade-signals-refresh-fail')
    expect(wrapper.findAll('.artdeco-trading-signals__row')).toHaveLength(2)
    expect(wrapper.text()).toContain('trade signals refresh unavailable')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的交易信号快照。')
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('宁德时代')
  })
})
