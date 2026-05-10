import { flushPromises, mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const errorMock = ref(null as string | null)
const loadingMock = ref(false)
const lastRequestIdMock = ref('req-trade-portfolio')

const { getMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
}))

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: getMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    exec: async (
      apiCall: () => Promise<{ success?: boolean; data?: unknown; request_id?: string; message?: string }>
    ) => {
      loadingMock.value = true
      errorMock.value = null

      try {
        const response = await apiCall()
        lastRequestIdMock.value = response?.request_id ?? ''
        if (response?.success === false) {
          errorMock.value = response?.message ?? '组合资产加载失败'
          return null
        }
        return response?.data ?? response
      } catch (requestError: unknown) {
        errorMock.value = requestError instanceof Error ? requestError.message : '组合资产加载失败'
        return null
      } finally {
        loadingMock.value = false
      }
    },
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      template: '<button @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
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

import TradePortfolioPage from '../Portfolio.vue'

function mountPortfolioPage() {
  return mount(TradePortfolioPage as never, {
    global: {
      stubs: {
      },
      directives: {
        loading: {},
      },
    },
  })
}

describe('TradePortfolio routed policy truth', () => {
  beforeEach(() => {
    errorMock.value = null
    loadingMock.value = false
    lastRequestIdMock.value = 'req-trade-portfolio'
    getMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-trade-portfolio',
      data: {
        positions: [
          {
            symbol: '600519',
            symbol_name: '贵州茅台',
            market_value: 202584,
            profit_loss_percent: -0.69,
          },
          {
            symbol: '300750',
            symbol_name: '宁德时代',
            market_value: 170080,
            profit_loss_percent: 1.24,
          },
        ],
        total_market_value: 372664,
        total_profit_loss: 6844,
        total_profit_loss_percent: 1.84,
      },
    })
  })

  it('does not present auto rebalance actions as real strategy advice when the live payload has no target-weight policy input', async () => {
    const wrapper = mountPortfolioPage()

    await flushPromises()

    expect(getMock).toHaveBeenCalledWith('/v1/trade/positions')
    expect(wrapper.find('.hero-meta').text()).toContain('POSITIONS: 2')
    expect(wrapper.find('.hero-meta').text()).toContain('REBALANCE: 待接入')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['372,664.00', '+6,844', '2', '待接入'])
    expect(wrapper.find('.stats-strip').text()).not.toContain('2.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('+0%')
    expect(wrapper.text()).toContain('再平衡策略待接入，当前持仓数据未提供目标仓位或组合约束。')
    expect(wrapper.text()).not.toContain('当前 54.36% → 目标 25%')
    expect(wrapper.text()).not.toContain('建议减仓约')
  })

  it('renders the canonical attribution panel from the positions attribution endpoint', async () => {
    getMock.mockImplementation((url: string) => {
      if (url === '/v1/positions/attribution') {
        return Promise.resolve({
          success: true,
          request_id: 'req-position-attribution',
          data: {
            analysis_date: '2026-05-08',
            snapshot_meta: {
              stale: true,
              stale_reason: 'runtime_position_prices',
              total_return: 0.0312,
              constituent_count: 2,
            },
            benchmark_meta: {
              total_return: 0.018,
              constituent_count: 3,
            },
            brinson: {
              allocation_effect: 0.004,
              selection_effect: 0.007,
              interaction_effect: 0.002,
              industry_breakdown: {
                银行: {
                  portfolio_weight: 0.62,
                  benchmark_weight: 0.4,
                  allocation_effect: 0.004,
                  selection_effect: 0.003,
                },
              },
            },
            factor_attribution: {
              factor_exposures: {
                size: {
                  portfolio_exposure: 0.31,
                  benchmark_exposure: 0.12,
                  active_exposure: 0.19,
                },
              },
              factor_contributions: {
                size: 0.0038,
              },
              specific_return: 0.0042,
            },
            top_contributors: [
              {
                symbol: '600519',
                industry: '食品饮料',
                weight: 0.54,
                return_rate: 0.08,
                contribution_value: 0.0432,
              },
            ],
            top_detractors: [
              {
                symbol: '300750',
                industry: '新能源',
                weight: 0.46,
                return_rate: -0.01,
                contribution_value: -0.0046,
              },
            ],
          },
        })
      }

      return Promise.resolve({
        success: true,
        request_id: 'req-trade-portfolio',
        data: {
          positions: [
            {
              symbol: '600519',
              symbol_name: '贵州茅台',
              market_value: 202584,
              profit_loss_percent: -0.69,
            },
            {
              symbol: '300750',
              symbol_name: '宁德时代',
              market_value: 170080,
              profit_loss_percent: 1.24,
            },
          ],
          total_market_value: 372664,
          total_profit_loss: 6844,
          total_profit_loss_percent: 1.84,
        },
      })
    })

    const wrapper = mountPortfolioPage()

    await flushPromises()

    expect(getMock).toHaveBeenCalledWith('/v1/positions/attribution', { params: {} })
    expect(wrapper.text()).toContain('Brinson 归因')
    expect(wrapper.text()).toContain('五因子归因')
    expect(wrapper.text()).toContain('runtime_position_prices')
    expect(wrapper.text()).toContain('600519')
  })

  it('requests date-scoped attribution when the attribution date control changes', async () => {
    getMock.mockImplementation((url: string, config?: { params?: Record<string, string> }) => {
      if (url === '/v1/positions/attribution') {
        return Promise.resolve({
          success: true,
          request_id: config?.params?.date ? 'req-position-attribution-date' : 'req-position-attribution-current',
          data: {
            analysis_date: config?.params?.date || '2026-05-10',
            snapshot_meta: {
              stale: !config?.params?.date,
              stale_reason: config?.params?.date ? null : 'runtime_position_prices',
              total_return: 0.0312,
              constituent_count: 2,
            },
            benchmark_meta: {
              total_return: 0.018,
              constituent_count: 3,
            },
            brinson: {
              allocation_effect: 0.004,
              selection_effect: 0.007,
              interaction_effect: 0.002,
              industry_breakdown: {},
            },
            factor_attribution: {
              factor_exposures: {},
              factor_contributions: {},
              specific_return: 0.0042,
            },
            top_contributors: [],
            top_detractors: [],
          },
        })
      }

      return Promise.resolve({
        success: true,
        request_id: 'req-trade-portfolio',
        data: {
          positions: [
            {
              symbol: '600519',
              symbol_name: '贵州茅台',
              market_value: 202584,
              profit_loss_percent: -0.69,
            },
            {
              symbol: '300750',
              symbol_name: '宁德时代',
              market_value: 170080,
              profit_loss_percent: 1.24,
            },
          ],
          total_market_value: 372664,
          total_profit_loss: 6844,
          total_profit_loss_percent: 1.84,
        },
      })
    })

    const wrapper = mountPortfolioPage()

    await flushPromises()

    expect(getMock).toHaveBeenCalledWith('/v1/positions/attribution', { params: {} })

    await wrapper.get('[data-testid="attribution-mode-date"]').trigger('click')
    await wrapper.get('[data-testid="attribution-date-input"]').setValue('2026-05-08')
    await wrapper.get('[data-testid="attribution-date-input"]').trigger('change')
    await flushPromises()

    expect(getMock).toHaveBeenCalledWith('/v1/positions/attribution', {
      params: {
        date: '2026-05-08',
      },
    })
    expect(wrapper.text()).toContain('2026-05-08')
    expect(wrapper.text()).not.toContain('runtime_position_prices')
  })

  it('keeps first-load portfolio summary surfaces in pending placeholders instead of fabricated zero balances and false empty-state copy', async () => {
    getMock.mockImplementation(() => new Promise(() => {}))

    const wrapper = mountPortfolioPage()

    await nextTick()

    expect(wrapper.find('.hero-meta').text()).toContain('POSITIONS: --')
    expect(wrapper.find('.hero-meta').text()).toContain('REBALANCE: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.find('.assets-hero').text()).toContain('Total Assets (CNY)--')
    expect(wrapper.find('.assets-hero').text()).toContain("Today's P&L--")
    expect(wrapper.text()).toContain('组合资产同步中...')
    expect(wrapper.text()).not.toContain('暂无持仓数据。')
    expect(wrapper.text()).not.toContain('再平衡策略待接入')
    expect(wrapper.text()).not.toContain('0.00')
    expect(wrapper.text()).not.toContain('+0%')
  })

  it('does not present failed first-load portfolio summary surfaces as faux zero balances or false empty-state copy', async () => {
    getMock.mockRejectedValue(new Error('positions unavailable'))

    const wrapper = mountPortfolioPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('POSITIONS: --')
    expect(wrapper.find('.hero-meta').text()).toContain('REBALANCE: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.find('.assets-hero').text()).toContain('Total Assets (CNY)--')
    expect(wrapper.find('.assets-hero').text()).toContain("Today's P&L--")
    expect(wrapper.text()).toContain('positions unavailable')
    expect(wrapper.text()).not.toContain('暂无持仓数据。')
    expect(wrapper.text()).not.toContain('再平衡策略待接入')
    expect(wrapper.text()).not.toContain('0.00')
    expect(wrapper.text()).not.toContain('+0%')
  })

  it('does not leak a failed first-load portfolio request id before any verified snapshot exists', async () => {
    lastRequestIdMock.value = ''
    getMock.mockReset()
    getMock.mockResolvedValueOnce({
      success: false,
      message: 'positions unavailable',
      request_id: 'portfolio-first-fail',
    })

    const wrapper = mountPortfolioPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('POSITIONS: --')
    expect(wrapper.find('.hero-meta').text()).toContain('REBALANCE: --')
    expect(wrapper.text()).not.toContain('portfolio-first-fail')
  })

  it('keeps the last verified portfolio request id visible when a manual refresh fails', async () => {
    lastRequestIdMock.value = ''
    getMock.mockReset()
    getMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'portfolio-success-snapshot',
        data: {
          positions: [
            {
              symbol: '600519',
              symbol_name: '贵州茅台',
              market_value: 202584,
              profit_loss_percent: -0.69,
            },
            {
              symbol: '300750',
              symbol_name: '宁德时代',
              market_value: 170080,
              profit_loss_percent: 1.24,
            },
          ],
          total_market_value: 372664,
          total_profit_loss: 6844,
          total_profit_loss_percent: 1.84,
        },
      })
      .mockResolvedValueOnce({
        success: true,
        request_id: 'attribution-success-snapshot',
        data: {
          analysis_date: '2026-05-08',
          snapshot_meta: { total_return: 0.018, constituent_count: 2, stale: false },
          benchmark_meta: { total_return: 0.012, constituent_count: 3 },
          brinson: {},
          factor_attribution: {},
          top_contributors: [],
          top_detractors: [],
        },
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'positions refresh unavailable',
        request_id: 'portfolio-refresh-fail',
      })

    const wrapper = mountPortfolioPage()

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ: portfolio-success-snapshot')
    expect(wrapper.find('.hero-meta').text()).not.toContain('portfolio-refresh-fail')
    expect(wrapper.find('.hero-meta').text()).toContain('POSITIONS: 2')
    expect(wrapper.text()).toContain('positions refresh unavailable')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的组合快照')
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('宁德时代')
  })

  it('hides route-level hero and stats shells when embedded in an outer trading shell', async () => {
    const wrapper = mount(TradePortfolioPage as never, {
      props: {
        functionKey: 'trade-portfolio-shell',
      },
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.classes()).toContain('is-embedded')
    expect(wrapper.find('.hero-shell').exists()).toBe(false)
    expect(wrapper.find('.stats-strip').exists()).toBe(false)
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).toContain('宁德时代')
  })
})
