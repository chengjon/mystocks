import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getAlertRulesMock,
  getAlertsMock,
  loadingMock,
  errorMock,
  lastRequestIdMock,
} = vi.hoisted(() => ({
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  ...(() => {
    const { ref } = require('vue')
    return {
      loadingMock: ref(false),
      errorMock: ref(null as string | null),
      lastRequestIdMock: ref(''),
    }
  })(),
  getAlertRulesMock: vi.fn(),
  getAlertsMock: vi.fn(),
}))

vi.mock('@/api/index', () => ({
  monitoringApi: {
    getAlertRules: getAlertRulesMock,
    getAlerts: getAlertsMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    exec: async (
      apiCall: () => Promise<{ success?: boolean; data?: unknown; request_id?: string }>,
      options: { errorMsg?: string } = {},
    ) => {
      const response = await apiCall()
      lastRequestIdMock.value = response?.request_id || ''
      if (response?.success === false) {
        errorMock.value = options.errorMsg || (typeof (response as { message?: unknown })?.message === 'string'
          ? (response as { message?: string }).message || null
          : '操作失败')
        return null
      }
      errorMock.value = null
      return response?.data ?? response
    },
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')
  const { default: ArtDecoTable } = await import('@/components/artdeco/trading/ArtDecoTable.vue')

  return {
    ArtDecoButton: {
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
    ArtDecoTable,
  }
})

import RiskOverviewPage from '../Overview.vue'

function mountOverviewPage() {
  return mount(RiskOverviewPage as never, {
    global: {
      stubs: {
      },
      directives: {
        loading: {},
      },
    },
  })
}

describe('RiskOverview routed data truth', () => {
  beforeEach(() => {
    errorMock.value = null
    lastRequestIdMock.value = 'req-risk-overview'
    getAlertRulesMock.mockReset().mockResolvedValue({
      success: true,
      data: [
        {
          id: 1,
          rule_name: '单票止损线',
          rule_type: 'stop_loss',
          symbol: '600519',
          is_active: true,
          priority: 1,
        },
      ],
      request_id: 'req-risk-rules',
    })
    getAlertsMock.mockReset().mockResolvedValue({
      success: true,
      data: [],
      request_id: 'req-risk-alerts-empty',
    })
  })

  it('uses live alerts data for the alert tab and shows an honest empty state when no records exist', async () => {
    const wrapper = mountOverviewPage()

    await flushPromises()

    const alertTab = wrapper.findAll('button').find((button) => button.text().includes('预警消息'))
    expect(alertTab).toBeDefined()
    await alertTab!.trigger('click')
    await flushPromises()

    expect(getAlertsMock).toHaveBeenCalledWith({ page: 1, page_size: 50 })
    expect(wrapper.text()).toContain('ALERTS: 0')
    expect(wrapper.text()).toContain('今日告警0')
    expect(wrapper.text()).toContain('暂无预警消息。')
    expect(wrapper.text()).not.toContain('组合波动率超过阈值 18%')
    expect(wrapper.text()).not.toContain('单票仓位接近上限 9.6%')
    expect(wrapper.text()).not.toContain('北向资金流入放缓')
  })

  it('does not present unverified overview metrics as real runtime values', async () => {
    const wrapper = mountOverviewPage()

    await flushPromises()

    expect(wrapper.text()).toContain('仓位集中度未校验')
    expect(wrapper.text()).toContain('组合Beta未校验待接入')
    expect(wrapper.text()).toContain('波动率(20日)未校验待接入')
    expect(wrapper.text()).toContain('最大回撤(近3月)未校验待接入')
    expect(wrapper.text()).toContain('VaR(95%)未校验待接入')
    expect(wrapper.text()).not.toContain('38.6%')
    expect(wrapper.text()).not.toContain('1.08')
    expect(wrapper.text()).not.toContain('16.2%')
    expect(wrapper.text()).not.toContain('-8.9%')
    expect(wrapper.text()).not.toContain('2.6%')
  })

  it('does not render rule and alert tally cards as faux delta metrics with fabricated decimal precision', async () => {
    const wrapper = mountOverviewPage()

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '0', '未校验'])
    expect(wrapper.text()).not.toContain('+0%')
    expect(wrapper.text()).not.toContain('1.00')
    expect(wrapper.text()).not.toContain('0.00')
  })

  it('renders rule priorities as ordinal integers instead of fabricated decimal metrics', async () => {
    const wrapper = mountOverviewPage()

    await flushPromises()

    const rulesTab = wrapper.findAll('button').find((button) => button.text().includes('规则清单'))
    expect(rulesTab).toBeDefined()
    await rulesTab!.trigger('click')
    await flushPromises()

    const ruleTable = wrapper.get('.hybrid-table__content')
    expect(ruleTable.text()).toContain('单票止损线')
    expect(ruleTable.text()).toContain('1')
    expect(ruleTable.text()).not.toContain('1.00')
  })

  it('does not leak a failed first-load risk overview request id before any verified snapshot exists', async () => {
    getAlertRulesMock.mockResolvedValueOnce({
      success: false,
      message: 'risk rules unavailable',
      request_id: 'req-risk-rules-first-fail',
      data: null,
    })
    getAlertsMock.mockResolvedValueOnce({
      success: false,
      message: 'risk alerts unavailable',
      request_id: 'req-risk-alerts-first-fail',
      data: null,
    })

    const wrapper = mountOverviewPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('ALERTS: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('获取预警记录失败')
    expect(wrapper.text()).not.toContain('req-risk-rules-first-fail')
    expect(wrapper.text()).not.toContain('req-risk-alerts-first-fail')
    expect(wrapper.text()).not.toContain('今日告警0')
  })

  it('keeps the last verified overview request id and visible rows when a manual refresh fails', async () => {
    getAlertRulesMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-risk-rules-success',
        data: [
          {
            id: 1,
            rule_name: '单票止损线',
            rule_type: 'stop_loss',
            symbol: '600519',
            is_active: true,
            priority: 1,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'risk rules refresh unavailable',
        request_id: 'req-risk-rules-refresh-fail',
        data: null,
      })
    getAlertsMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-risk-alerts-success',
        data: [
          {
            id: 9,
            alert_level: 'warning',
            alert_message: '已跌破止损线，请立即处理。',
            rule_name: '单票止损线',
            alert_time: '2026-04-26T09:35:00Z',
          },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'risk alerts refresh unavailable',
        request_id: 'req-risk-alerts-refresh-fail',
        data: null,
      })

    const wrapper = mountOverviewPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-risk-alerts-success')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '1', '未校验'])

    await wrapper.findAll('button').find((button) => button.text().includes('刷新概览'))!.trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-risk-alerts-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-risk-rules-refresh-fail')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-risk-alerts-refresh-fail')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '1', '未校验'])
    expect(wrapper.text()).toContain('获取预警记录失败')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的风险概览快照。')

    const rulesTab = wrapper.findAll('button').find((button) => button.text().includes('规则清单'))
    expect(rulesTab).toBeDefined()
    await rulesTab!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('单票止损线')
  })

  it('shows the verified rules slice when alerts are still unavailable on the first load', async () => {
    getAlertRulesMock.mockResolvedValueOnce({
      success: true,
      request_id: 'req-risk-rules-first-success',
      data: [
        {
          id: 1,
          rule_name: '单票止损线',
          rule_type: 'stop_loss',
          symbol: '600519',
          is_active: true,
          priority: 1,
        },
      ],
    })
    getAlertsMock.mockResolvedValueOnce({
      success: false,
      message: 'risk alerts unavailable',
      request_id: 'req-risk-alerts-first-fail',
      data: null,
    })

    const wrapper = mountOverviewPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('ALERTS: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '--', '未校验'])

    const rulesTab = wrapper.findAll('button').find((button) => button.text().includes('规则清单'))
    expect(rulesTab).toBeDefined()
    await rulesTab!.trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-risk-rules-first-success')
    expect(wrapper.get('.content-shell-meta').text()).toContain('RULES: 1')
    expect(wrapper.get('.hybrid-table__content').text()).toContain('单票止损线')
    expect(wrapper.text()).toContain('获取预警记录失败')
    expect(wrapper.text()).toContain('当前预警消息暂不可用')
    expect(wrapper.text()).not.toContain('当前暂无已验证风险概览快照。')
  })
})
