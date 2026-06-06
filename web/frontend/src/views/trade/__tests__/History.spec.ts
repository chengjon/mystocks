import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { describe, expect, it, vi } from 'vitest'

const { apiGetMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn(),
}))

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: apiGetMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => {
    const state = {
      loading: ref(false),
      error: ref<string | null>(null),
      lastRequestId: ref(''),
      lastProcessTime: ref(''),
      exec: async (
        apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string; process_time_ms?: number }>
      ) => {
        state.loading.value = true
        state.error.value = null

        try {
          const response = await apiCall()
          state.lastRequestId.value = response?.request_id ?? ''
          state.lastProcessTime.value = response?.process_time_ms ? String(response.process_time_ms) : ''

          if (response?.success === false) {
            state.error.value = response.message ?? '请求失败'
            return null
          }

          return response?.data ?? response
        } catch (error: unknown) {
          state.error.value = error instanceof Error ? error.message : '请求失败'
          return null
        } finally {
          state.loading.value = false
        }
      },
    }

    return state
  },
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['loading', 'disabled'],
      emits: ['click'],
      template: '<button @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
  }
})

import TradeHistoryPage from '../History.vue'

describe('Trade history stale refresh truth', () => {
  it('does not present trade history as verified zero rows while the first ledger payload is still unresolved', async () => {
    apiGetMock.mockReset().mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(TradeHistoryPage as never)

    await Promise.resolve()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('TIME: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('ROWS: --')
    expect(wrapper.get('.hero-meta').text()).not.toContain('ROWS: 0')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('交易历史同步中...')
  })

  it('does not present failed first-load trade history as a verified empty ledger before any snapshot exists', async () => {
    apiGetMock.mockReset().mockResolvedValueOnce({
      success: false,
      request_id: 'trade-history-first-fail',
      process_time_ms: 19,
      message: '交易历史接口失败',
    })

    const wrapper = mount(TradeHistoryPage as never)

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('TIME: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('ROWS: --')
    expect(wrapper.get('.hero-meta').text()).not.toContain('ROWS: 0')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('交易历史接口失败')
    expect(wrapper.text()).not.toContain('暂无历史成交记录')
  })

  it('keeps the last successful trade ledger visible when a manual refresh fails', async () => {
    apiGetMock.mockReset()
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'trade-history-initial-ok',
        process_time_ms: 18,
        data: {
          trades: [
            {
              trade_id: 'trade-001',
              symbol: '600519',
              direction: 'buy',
              price: 1688.2,
              quantity: 20,
              amount: 33764,
              commission: 16.8,
              trade_time: '2026-04-03T09:41:05Z',
              status: 'completed',
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        success: false,
        request_id: 'trade-history-refresh-fail',
        message: '交易历史接口失败',
      })

    const wrapper = mount(TradeHistoryPage as never, {
      global: {},
    })

    await flushPromises()

    expect(wrapper.text()).toContain('600519')
    expect(wrapper.text()).toContain('已成交')

    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(apiGetMock).toHaveBeenCalledTimes(2)
    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: trade-history-initial-ok')
    expect(wrapper.get('.hero-meta').text()).toContain('TIME: 18.00ms')
    expect(wrapper.get('.hero-meta').text()).not.toContain('REQ_ID: trade-history-refresh-fail')
    expect(wrapper.text()).toContain('刷新异常')
    expect(wrapper.text()).toContain('当前仍展示上次成功同步的交易历史记录。')
    expect(wrapper.text()).toContain('600519')
    expect(wrapper.text()).toContain('已成交')
    expect(wrapper.findAll('.artdeco-trading-history__row')).toHaveLength(1)
    expect(wrapper.text()).not.toContain('交易历史拉取失败，当前无法展示真实记录。')
  })

  it('does not render trade-history tally cards as faux delta metrics with fabricated decimal precision', async () => {
    apiGetMock.mockReset().mockResolvedValueOnce({
      success: true,
      request_id: 'trade-history-kpi-ok',
      process_time_ms: 21,
      data: {
        trades: [
          {
            trade_id: 'trade-001',
            symbol: '600519',
            direction: 'buy',
            price: 1688.2,
            quantity: 20,
            amount: 33764,
            commission: 16.8,
            trade_time: '2026-04-03T09:41:05Z',
            status: 'completed',
          },
          {
            trade_id: 'trade-002',
            symbol: '300750',
            direction: 'sell',
            price: 212.5,
            quantity: 10,
            amount: 2125,
            commission: 3.2,
            trade_time: '2026-04-03T10:15:09Z',
            status: 'pending',
          },
        ],
      },
    })

    const wrapper = mount(TradeHistoryPage as never)

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['2', '1', '1', '¥35889'])
    expect(wrapper.get('.stats-strip').text()).not.toContain('+0%')
    expect(wrapper.get('.stats-strip').text()).not.toContain('2.00')
    expect(wrapper.get('.stats-strip').text()).not.toContain('1.00')
  })

  it('hides route-level hero and stats shells when embedded in an outer trading shell', async () => {
    apiGetMock.mockReset()

    const wrapper = mount(TradeHistoryPage as never, {
      props: {
        history: [
          {
            id: 'trade-embedded-001',
            time: '2026-04-03 09:41:05',
            symbol: '600519',
            symbolName: '贵州茅台',
            type: 'buy',
            typeText: '买入',
            price: 1688.2,
            quantity: 20,
            amount: 33764,
            fee: 16.8,
            status: 'completed',
            statusText: '已成交',
          },
        ],
      },
    })

    await flushPromises()

    expect(wrapper.classes()).toContain('is-embedded')
    expect(wrapper.find('.hero-shell').exists()).toBe(false)
    expect(wrapper.find('.stats-strip').exists()).toBe(false)
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('已成交')
  })
})
