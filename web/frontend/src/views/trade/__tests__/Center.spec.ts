import { flushPromises, mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
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
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
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

import TradeCenterPage from '@/views/trade/Center.vue'

describe('Trade positions routed numeric truth', () => {
  beforeEach(() => {
    apiGetMock.mockReset()
  })

  it('does not present unresolved first-load position tallies and totals as faux zero metrics or fallback request labels', async () => {
    apiGetMock.mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mount(TradeCenterPage as never)

    await nextTick()
    await nextTick()

    expect(wrapper.get('.hero-meta').text()).toContain('请求: --')
    expect(wrapper.get('.hero-meta').text()).toContain('耗时: --')
    expect(wrapper.get('.hero-meta').text()).toContain('行数: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('市值: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('总盈亏: --')

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(statsStrip.text()).not.toContain('+0%')
    expect(statsStrip.text()).not.toContain('0.00')
    expect(statsStrip.text()).not.toContain('N/A')
  })

  it('does not render empty resolved position tally cards as faux delta metrics with fabricated decimal precision', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: true,
      request_id: 'trade-positions-empty-ok',
      process_time_ms: 31,
      data: {
        positions: [],
        total_market_value: 0,
      },
    })

    const wrapper = mount(TradeCenterPage as never)

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('请求: trade-positions-empty-ok')
    expect(wrapper.get('.hero-meta').text()).toContain('耗时: 31.00ms')
    expect(wrapper.get('.hero-meta').text()).toContain('行数: 0')
    expect(wrapper.get('.content-shell-meta').text()).toContain('市值: ¥0')
    expect(wrapper.get('.content-shell-meta').text()).toContain('总盈亏: ¥0')

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['0', '0', '0', '¥0'])
    expect(statsStrip.text()).not.toContain('+0%')
    expect(statsStrip.text()).not.toContain('0.00')
  })

  it('does not leak a failed first-load positions request id before any verified snapshot exists', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: false,
      message: 'positions unavailable',
      request_id: 'trade-positions-first-fail',
    })

    const wrapper = mount(TradeCenterPage as never)

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('请求: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('行数: --')
    expect(wrapper.text()).toContain('持仓拉取失败')
    expect(wrapper.text()).not.toContain('trade-positions-first-fail')
  })

  it('keeps the last verified positions request id and visible rows when a manual refresh fails', async () => {
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'trade-positions-success',
        process_time_ms: 31,
        data: {
          positions: [
            {
              symbol: '600519',
              symbol_name: '贵州茅台',
              quantity: 120,
              cost_price: 1660.5,
              current_price: 1688.2,
              market_value: 202584,
              profit_loss: 3324,
              profit_loss_percent: 1.67,
            },
            {
              symbol: '300750',
              symbol_name: '宁德时代',
              quantity: 800,
              cost_price: 208.2,
              current_price: 212.6,
              market_value: 170080,
              profit_loss: 3520,
              profit_loss_percent: 2.11,
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'positions refresh unavailable',
        request_id: 'trade-positions-refresh-fail',
      })

    const wrapper = mount(TradeCenterPage as never)

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('请求: trade-positions-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('trade-positions-refresh-fail')
    expect(wrapper.get('.hero-meta').text()).toContain('耗时: 31.00ms')
    expect(wrapper.get('.hero-meta').text()).toContain('行数: 2')
    expect(wrapper.text()).toContain('positions refresh unavailable')
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('宁德时代')
    expect(wrapper.findAll('.artdeco-trading-positions__row')).toHaveLength(2)
  })

  it('segments verified positions into loss and attention review lenses with stable hooks', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: true,
      request_id: 'trade-positions-segments-ok',
      process_time_ms: 24,
      data: {
        total_market_value: 300000,
        positions: [
          {
            symbol: '600519',
            symbol_name: '贵州茅台',
            quantity: 60,
            cost_price: 1700,
            current_price: 1688,
            market_value: 101280,
            profit_loss: -720,
            profit_loss_percent: -0.71,
          },
          {
            symbol: '300750',
            symbol_name: '宁德时代',
            quantity: 800,
            cost_price: 208.2,
            current_price: 212.6,
            market_value: 170080,
            profit_loss: 3520,
            profit_loss_percent: 2.11,
          },
          {
            symbol: '510300',
            symbol_name: '沪深300ETF',
            quantity: 7000,
            cost_price: 3.8,
            current_price: 3.76,
            market_value: 26320,
            profit_loss: -280,
            profit_loss_percent: -1.05,
          },
        ],
      },
    })

    const wrapper = mount(TradeCenterPage as never)

    await flushPromises()

    expect(wrapper.get('[data-test="trade-positions-runtime"]').text()).toContain('已验证')
    expect(wrapper.findAll('[data-test="trade-positions-row"]')).toHaveLength(3)

    await wrapper.get('[data-segment="loss"]').trigger('click')
    expect(wrapper.get('[data-test="trade-positions-runtime"]').text()).toContain('当前显示 亏损 持仓 2 条')
    expect(wrapper.findAll('[data-test="trade-positions-row"]')).toHaveLength(2)
    expect(wrapper.get('[data-test="trade-positions-table"]').text()).toContain('贵州茅台')
    expect(wrapper.get('[data-test="trade-positions-table"]').text()).toContain('沪深300ETF')
    expect(wrapper.get('[data-test="trade-positions-table"]').text()).not.toContain('宁德时代')

    await wrapper.get('[data-segment="highWeight"]').trigger('click')
    expect(wrapper.get('[data-test="trade-positions-runtime"]').text()).toContain('当前显示 高仓位 持仓 2 条')
    expect(wrapper.findAll('[data-test="trade-positions-row"]')).toHaveLength(2)
  })
})
