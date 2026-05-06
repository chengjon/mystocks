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
      apiCall: () => Promise<{ success?: boolean; data?: unknown; request_id?: string; message?: string }>,
      options: { errorMsg?: string } = {},
    ) => {
      const response = await apiCall()
      lastRequestIdMock.value = response?.request_id || ''
      if (response?.success === false) {
        errorMock.value = options.errorMsg || (typeof response?.message === 'string' ? response.message || null : '操作失败')
        return null
      }
      errorMock.value = null
      return response?.data ?? response
    },
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

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
  }
})

import RiskAlertsPage from '../Alerts.vue'

function mountAlertsPage() {
  return mount(RiskAlertsPage as never, {
    global: {
      stubs: {
        ArtDecoCard: {
          props: ['title'],
          template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
        },
        'el-table': {
          props: ['data'],
          template: '<div class="el-table-stub">{{ JSON.stringify(data) }}</div>',
        },
        'el-table-column': {
          template: '<div />',
        },
        'el-tag': {
          template: '<span><slot /></span>',
        },
      },
      directives: {
        loading: {},
      },
    },
  })
}

describe('RiskAlerts routed count-kpi truth', () => {
  beforeEach(() => {
    loadingMock.value = false
    errorMock.value = null
    lastRequestIdMock.value = 'req-risk-alerts'
    getAlertRulesMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-alert-rules',
      data: [
        {
          id: 1,
          rule_name: '单票止损线',
          rule_type: 'stop_loss',
          symbol: '600519',
          is_active: true,
          updated_at: '2026-04-01T08:30:00Z',
        },
      ],
    })
    getAlertsMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-alert-records',
      data: [
        {
          id: 10,
          symbol: '600519',
          stock_name: '贵州茅台',
          alert_type: 'stop_loss',
          alert_level: 'critical',
          alert_message: '已跌破止损线，请立即处理。',
          is_read: false,
          alert_time: '2026-04-01T09:31:00Z',
        },
      ],
    })
  })

  it('does not render alert-count stat cards as faux delta metrics with +0 percent chrome', async () => {
    const wrapper = mountAlertsPage()

    await flushPromises()

    expect(getAlertRulesMock).toHaveBeenCalledTimes(1)
    expect(getAlertsMock).toHaveBeenCalledWith({ page: 1, page_size: 50 })
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '1', '1'])
    expect(wrapper.text()).not.toContain('+0%')
    expect(wrapper.text()).not.toContain('1.00')
  })

  it('does not leak a failed first-load risk alerts request id before any verified snapshot exists', async () => {
    getAlertRulesMock.mockResolvedValueOnce({
      success: false,
      message: 'risk rules unavailable',
      request_id: 'req-risk-alerts-rules-first-fail',
      data: null,
    })
    getAlertsMock.mockResolvedValueOnce({
      success: false,
      message: 'risk alerts unavailable',
      request_id: 'req-risk-alerts-records-first-fail',
      data: null,
    })

    const wrapper = mountAlertsPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('UNREAD: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('RULES: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('ALERTS: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(wrapper.text()).toContain('获取告警记录失败')
    expect(wrapper.text()).not.toContain('req-risk-alerts-rules-first-fail')
    expect(wrapper.text()).not.toContain('req-risk-alerts-records-first-fail')
    expect(wrapper.text()).not.toContain('暂无告警记录，近期告警面板为空。')
    expect(wrapper.text()).not.toContain('暂无风险告警规则。')
  })

  it('keeps verified rules visible when alert records fail on the first load before any full snapshot exists', async () => {
    getAlertRulesMock.mockResolvedValueOnce({
      success: true,
      request_id: 'req-risk-alerts-rules-first-success',
      data: [
        {
          id: 1,
          rule_name: '组合波动率约束',
          rule_type: 'portfolio_volatility',
          symbol: 'GLOBAL',
          is_active: true,
          updated_at: '2026-04-01T08:40:00Z',
        },
      ],
    })
    getAlertsMock.mockResolvedValueOnce({
      success: false,
      message: 'risk alerts unavailable',
      request_id: 'req-risk-alerts-records-first-fail',
      data: null,
    })

    const wrapper = mountAlertsPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('UNREAD: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('RULES: 1')
    expect(wrapper.get('.content-shell-meta').text()).toContain('ALERTS: --')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '--', '--'])
    expect(wrapper.text()).toContain('获取告警记录失败')
    expect(wrapper.text()).toContain('当前告警记录暂不可用。')
    expect(wrapper.text()).toContain('组合波动率约束')
    expect(wrapper.text()).not.toContain('req-risk-alerts-rules-first-success')
    expect(wrapper.text()).not.toContain('req-risk-alerts-records-first-fail')
    expect(wrapper.text()).not.toContain('已跌破止损线，请立即处理。')
    expect(wrapper.text()).not.toContain('当前暂无已验证告警快照。')
  })

  it('keeps the last verified alerts request id and visible rows when a manual refresh fails', async () => {
    getAlertRulesMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-risk-alerts-rules-success',
        data: [
          {
            id: 1,
            rule_name: '组合波动率约束',
            rule_type: 'portfolio_volatility',
            symbol: 'GLOBAL',
            is_active: true,
            updated_at: '2026-04-01T08:40:00Z',
          },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'risk rules refresh unavailable',
        request_id: 'req-risk-alerts-rules-refresh-fail',
        data: null,
      })
    getAlertsMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-risk-alerts-success',
        data: [
          {
            id: 10,
            symbol: '600519',
            stock_name: '贵州茅台',
            alert_type: 'stop_loss',
            alert_level: 'critical',
            alert_message: '已跌破止损线，请立即处理。',
            is_read: false,
            alert_time: '2026-04-01T09:31:00Z',
          },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'risk alerts refresh unavailable',
        request_id: 'req-risk-alerts-refresh-fail',
        data: null,
      })

    const wrapper = mountAlertsPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-risk-alerts-success')
    expect(wrapper.get('.hero-meta').text()).toContain('UNREAD: 1')
    expect(wrapper.get('.content-shell-meta').text()).toContain('RULES: 1')
    expect(wrapper.get('.content-shell-meta').text()).toContain('ALERTS: 1')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '1', '1'])
    expect(wrapper.text()).toContain('组合波动率约束')
    expect(wrapper.text()).toContain('已跌破止损线，请立即处理。')

    await wrapper.findAll('button').find((button) => button.text().includes('刷新告警'))!.trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-risk-alerts-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-risk-alerts-rules-refresh-fail')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-risk-alerts-refresh-fail')
    expect(wrapper.get('.content-shell-meta').text()).toContain('RULES: 1')
    expect(wrapper.get('.content-shell-meta').text()).toContain('ALERTS: 1')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', '1', '1'])
    expect(wrapper.text()).toContain('获取告警记录失败')
    expect(wrapper.text()).toContain('组合波动率约束')
    expect(wrapper.text()).toContain('已跌破止损线，请立即处理。')
  })
})
