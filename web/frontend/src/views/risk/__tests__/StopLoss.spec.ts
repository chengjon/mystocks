import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

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
      exec: async (apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string }>) => {
        state.loading.value = true
        state.error.value = null

        try {
          const response = await apiCall()
          state.lastRequestId.value = response?.request_id ?? ''
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
      emits: ['click'],
      template: '<button @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
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

import RiskStopLossPage from '../StopLoss.vue'

function mountStopLossPage() {
  return mount(RiskStopLossPage as never, {
    global: {
      stubs: {
      },
      directives: {
        loading: {},
      },
    },
  })
}

describe('RiskStopLoss routed policy truth', () => {
  beforeEach(() => {
    apiGetMock.mockReset().mockImplementation(async (url: string) => {
      if (url === '/v1/monitoring/watchlists') {
        return {
          success: true,
          request_id: 'req-watchlists-1',
          data: [
            {
              id: 101,
              name: '核心止损监控',
              is_active: true,
            },
          ],
        }
      }

      if (url === '/v1/monitoring/watchlists/101/stocks') {
        return {
          success: true,
          request_id: 'req-watchlist-stocks-1',
          data: [
            {
              stock_code: '600519',
              stock_name: '贵州茅台',
              entry_price: 1820,
            },
          ],
        }
      }

      if (url === '/v1/market/quotes') {
        return {
          success: true,
          request_id: 'req-stoploss-quotes-1',
          data: [
            {
              symbol: '600519',
              name: '贵州茅台',
              current_price: 1805,
            },
          ],
        }
      }

      throw new Error(`Unhandled apiGetMock url: ${url}`)
    })
  })

  it('does not present watchlist quotes as active stop-loss monitoring when the live payload has no stop-loss threshold', async () => {
    const wrapper = mountStopLossPage()

    await flushPromises()

    expect(apiGetMock).toHaveBeenNthCalledWith(1, '/v1/monitoring/watchlists')
    expect(apiGetMock).toHaveBeenNthCalledWith(2, '/v1/monitoring/watchlists/101/stocks')
    expect(apiGetMock).toHaveBeenCalledWith('/v1/market/quotes', { params: { symbols: '600519' } })
    expect(wrapper.text()).toContain('策略待接入')
    expect(wrapper.text()).toContain('当前仅同步观察标的与行情，止损参数待接入。')
    expect(wrapper.text()).toContain('STOP LOSS待接入')
    expect(wrapper.text()).toContain('Distance to Stop待接入')
    expect(wrapper.text()).not.toContain('止损观察中')
    expect(wrapper.text()).not.toContain('Distance to Stop--%')
  })

  it('does not render stop-loss tally cards as faux delta metrics with fabricated decimal precision', async () => {
    const wrapper = mountStopLossPage()

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '0', '0', '--'])
    expect(wrapper.text()).not.toContain('+0%')
    expect(wrapper.text()).not.toContain('1.00')
    expect(wrapper.text()).not.toContain('0.00')
  })

  it('does not leak a failed first-load stop-loss request id before any verified snapshot exists', async () => {
    apiGetMock.mockReset()
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-1',
        data: [{ id: 101, name: '核心止损监控', is_active: true }],
      })
      .mockResolvedValueOnce({
        success: false,
        request_id: 'req-stoploss-first-fail',
        message: 'watchlist stocks unavailable',
        data: null,
      })

    const wrapper = mountStopLossPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('CRITICAL: --')
    expect(wrapper.find('.hero-meta').text()).toContain('TRIGGERED: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('watchlist stocks unavailable')
    expect(wrapper.text()).not.toContain('req-stoploss-first-fail')
    expect(wrapper.text()).not.toContain('暂无止损监控卡片')
  })

  it('keeps the last verified stop-loss request id visible when a manual refresh fails', async () => {
    apiGetMock.mockReset()
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-1',
        data: [{ id: 101, name: '核心止损监控', is_active: true }],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-stoploss-success',
        data: [
          {
            stock_code: '600519',
            stock_name: '贵州茅台',
            entry_price: 1820,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-stoploss-quotes-success',
        data: [
          {
            symbol: '600519',
            name: '贵州茅台',
            current_price: 1805,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-refresh',
        data: [{ id: 101, name: '核心止损监控', is_active: true }],
      })
      .mockResolvedValueOnce({
        success: false,
        request_id: 'req-stoploss-refresh-fail',
        message: 'watchlist stocks refresh unavailable',
        data: null,
      })

    const wrapper = mountStopLossPage()

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-stoploss-success')
    expect(wrapper.find('.hero-meta').text()).not.toContain('req-stoploss-refresh-fail')
    expect(wrapper.find('.hero-meta').text()).toContain('CRITICAL: 0')
    expect(wrapper.find('.hero-meta').text()).toContain('TRIGGERED: 0')
    expect(wrapper.text()).toContain('watchlist stocks refresh unavailable')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的止损快照')
    expect(wrapper.text()).toContain('贵州茅台')
  })

  it('does not leak the previous watchlist cards into a new primary watchlist without its own verified snapshot', async () => {
    apiGetMock.mockReset()
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-101',
        data: [{ id: 101, name: '核心止损监控', is_active: true }],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-stoploss-101-success',
        data: [
          {
            stock_code: '600519',
            stock_name: '贵州茅台',
            entry_price: 1820,
            stop_loss_price: 1750,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-stoploss-101-quotes',
        data: [
          {
            symbol: '600519',
            name: '贵州茅台',
            current_price: 1805,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-202',
        data: [
          { id: 202, name: '成长止损监控', is_active: true },
          { id: 101, name: '核心止损监控', is_active: false },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        request_id: 'req-stoploss-202-first-fail',
        message: 'watchlist 202 stocks unavailable',
        data: null,
      })

    const wrapper = mountStopLossPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-stoploss-101-success')
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.findAll('.risk-card')).toHaveLength(1)

    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('CRITICAL: --')
    expect(wrapper.find('.hero-meta').text()).toContain('TRIGGERED: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.findAll('.risk-card')).toHaveLength(0)
    expect(wrapper.text()).toContain('watchlist 202 stocks unavailable')
    expect(wrapper.text()).toContain('当前暂无已验证止损快照')
    expect(wrapper.text()).not.toContain('req-stoploss-101-success')
    expect(wrapper.text()).not.toContain('贵州茅台')
  })

  it('does not keep the previous watchlist cards visible while a new primary watchlist is still unresolved', async () => {
    let resolvePendingStocks: ((value: { success: boolean; request_id: string; data: unknown[] }) => void) | null = null
    const pendingStocksResponse = new Promise<{ success: boolean; request_id: string; data: unknown[] }>((resolve) => {
      resolvePendingStocks = resolve
    })

    apiGetMock.mockReset()
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-101',
        data: [{ id: 101, name: '核心止损监控', is_active: true }],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-stoploss-101-success',
        data: [
          {
            stock_code: '600519',
            stock_name: '贵州茅台',
            entry_price: 1820,
            stop_loss_price: 1750,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-stoploss-101-quotes',
        data: [
          {
            symbol: '600519',
            name: '贵州茅台',
            current_price: 1805,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-watchlists-202',
        data: [
          { id: 202, name: '成长止损监控', is_active: true },
          { id: 101, name: '核心止损监控', is_active: false },
        ],
      })
      .mockImplementationOnce(() => pendingStocksResponse)

    const wrapper = mountStopLossPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-stoploss-101-success')
    expect(wrapper.findAll('.risk-card')).toHaveLength(1)
    expect(wrapper.text()).toContain('贵州茅台')

    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('CRITICAL: --')
    expect(wrapper.find('.hero-meta').text()).toContain('TRIGGERED: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.findAll('.risk-card')).toHaveLength(0)
    expect(wrapper.text()).toContain('止损标的同步中')
    expect(wrapper.text()).not.toContain('贵州茅台')

    resolvePendingStocks?.({
      success: true,
      request_id: 'req-stoploss-202-success',
      data: [],
    })
  })
})
