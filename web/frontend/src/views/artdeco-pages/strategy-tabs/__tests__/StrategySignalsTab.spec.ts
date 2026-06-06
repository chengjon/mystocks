import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  refreshMock,
  loadingMock,
  errorMock,
  lastRequestIdMock,
  setActiveStrategyMock,
  getSnapshotMock,
  routeMock,
} = vi.hoisted(() => ({
  refreshMock: vi.fn(),
  loadingMock: { __v_isRef: true, value: false },
  errorMock: { __v_isRef: true, value: null as string | null },
  lastRequestIdMock: { __v_isRef: true, value: 'req-strategy-signals' },
  setActiveStrategyMock: vi.fn(),
  getSnapshotMock: vi.fn(() => null),
  routeMock: require('vue').reactive({
    query: {} as Record<string, unknown>,
  }),
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: () => ({
      loading: loadingMock,
      error: errorMock,
      lastRequestId: lastRequestIdMock,
    }),
  }
})

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
}))

vi.mock('@/stores/apiStores', () => ({
  useTradingSignalsStore: () => ({
    refresh: refreshMock,
  }),
}))

vi.mock('@/composables/strategy/useStrategyCrossTabContext', () => ({
  useStrategyCrossTabContext: () => ({
    getSnapshot: getSnapshotMock,
    setActiveStrategy: setActiveStrategyMock,
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['disabled', 'loading'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<div><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></div>',
    },
    ArtDecoIcon: {
      template: '<span class="artdeco-icon-stub" />',
    },
    ArtDecoStatCard,
  }
})

import StrategySignalsTab from '../StrategySignalsTab.vue'

function mountPage() {
  return mount(StrategySignalsTab as never, {
    global: {
      directives: {
        loading: {},
      },
    },
  })
}

describe('StrategySignals routed summary truth', () => {
  beforeEach(() => {
    refreshMock.mockReset().mockResolvedValue({
      data: [
        {
          signal_id: 'sig-001',
          symbol: '600519',
          name: '贵州茅台',
          type: 'BUY',
          price: 1688.2,
          time: '09:35:12',
          strategy: 'Momentum Alpha',
        },
        {
          signal_id: 'sig-002',
          symbol: '300750',
          name: '宁德时代',
          type: 'SELL',
          price: 212.6,
          time: '10:02:45',
          strategy: 'Reversion Beta',
        },
        {
          signal_id: 'sig-003',
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
    lastRequestIdMock.value = 'req-strategy-signals'
    setActiveStrategyMock.mockReset()
    getSnapshotMock.mockReset().mockReturnValue(null)
    routeMock.query = {}
  })

  it('does not render verified signal tallies as precise-decimal delta stats when the route only provides counts', async () => {
    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: 3')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['3', '1', '1', '1'])
    expect(wrapper.text()).not.toContain('3.00')
    expect(wrapper.text()).not.toContain('1.00')
    expect(wrapper.text()).not.toContain('+0%')
  })

  it('does not present failed first-load signal tallies as faux zero metrics', async () => {
    errorMock.value = 'strategy signals unavailable'
    refreshMock.mockRejectedValue(new Error('strategy signals unavailable'))

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.text()).toContain('策略信号加载失败')
    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).not.toContain('0.00')
    expect(wrapper.text()).not.toContain('+0%')
  })

  it('does not swallow resolved first-load failure envelopes into faux empty signal truth', async () => {
    refreshMock.mockResolvedValue({
      success: false,
      message: 'strategy signals unavailable',
      data: null,
    })

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.text()).toContain('策略信号加载失败')
    expect(wrapper.text()).toContain('strategy signals unavailable')
    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).not.toContain('当前暂无策略信号。')
  })

  it('keeps the last verified signal snapshot and request provenance when a refresh fails after success', async () => {
    refreshMock.mockReset()
    refreshMock
      .mockImplementationOnce(async () => {
        lastRequestIdMock.value = 'req-strategy-signals-success'
        return {
          data: [
            {
              signal_id: 'sig-001',
              symbol: '600519',
              name: '贵州茅台',
              type: 'BUY',
              price: 1688.2,
              time: '09:35:12',
              strategy: 'Momentum Alpha',
            },
            {
              signal_id: 'sig-002',
              symbol: '300750',
              name: '宁德时代',
              type: 'SELL',
              price: 212.6,
              time: '10:02:45',
              strategy: 'Reversion Beta',
            },
          ],
        }
      })
      .mockImplementationOnce(async () => {
        lastRequestIdMock.value = 'req-strategy-signals-refresh-fail'
        return {
          success: false,
          message: 'strategy signals refresh unavailable',
          data: null,
        }
      })

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-signals-success')
    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: 2')
    expect(wrapper.findAll('.signal-item')).toHaveLength(2)

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(refreshMock).toHaveBeenCalledTimes(2)
    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-signals-success')
    expect(wrapper.find('.hero-meta').text()).not.toContain('req-strategy-signals-refresh-fail')
    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: 2')
    expect(wrapper.findAll('.signal-item')).toHaveLength(2)
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('宁德时代')
  })

  it('does not leak the previous strategy signal rows into a new route query without its own verified snapshot', async () => {
    routeMock.query = { strategyId: '101' }
    refreshMock.mockReset()
    refreshMock.mockImplementation(async (params?: Record<string, unknown>) => {
      if (params?.strategy_id === '202') {
        lastRequestIdMock.value = 'req-strategy-signals-202-fail'
        return {
          success: false,
          message: 'strategy 202 signals unavailable',
          data: null,
        }
      }

      if (params?.strategy_id === '101') {
        lastRequestIdMock.value = 'req-strategy-signals-101'
        return {
          data: [
            {
              signal_id: 'sig-101-001',
              symbol: '600519',
              name: '贵州茅台',
              type: 'BUY',
              price: 1688.2,
              time: '09:35:12',
              strategy: 'Momentum Alpha',
            },
            {
              signal_id: 'sig-101-002',
              symbol: '002594',
              name: '比亚迪',
              type: 'HOLD',
              price: 258.3,
              time: '10:18:08',
              strategy: 'Momentum Alpha',
            },
          ],
        }
        }

      return { data: [] }
    })

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('FOCUS: 101')
    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: 2')
    expect(wrapper.findAll('.signal-item')).toHaveLength(2)
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('比亚迪')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(refreshMock).toHaveBeenCalled()
    expect(wrapper.find('.hero-meta').text()).toContain('FOCUS: 202')
    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.content-shell-meta').text()).toContain('COUNT: --')
    expect(wrapper.findAll('.signal-item')).toHaveLength(0)
    expect(wrapper.text()).toContain('策略信号加载失败')
    expect(wrapper.text()).toContain('strategy 202 signals unavailable')
    expect(wrapper.text()).not.toContain('贵州茅台')
    expect(wrapper.text()).not.toContain('比亚迪')
  })
})
