import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getAlertRulesMock,
  getAlertsMock,
  createAlertRuleMock,
  updateAlertRuleMock,
  deleteAlertRuleMock,
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
  createAlertRuleMock: vi.fn(),
  updateAlertRuleMock: vi.fn(),
  deleteAlertRuleMock: vi.fn(),
}))

vi.mock('@/api/index', () => ({
  monitoringApi: {
    getAlertRules: getAlertRulesMock,
    getAlerts: getAlertsMock,
    createAlertRule: createAlertRuleMock,
    updateAlertRule: updateAlertRuleMock,
    deleteAlertRule: deleteAlertRuleMock,
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
    createAlertRuleMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-alert-rule-create',
      data: { id: 2, rule_name: '新建规则' },
    })
    updateAlertRuleMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-alert-rule-update',
      data: { id: 1, rule_name: '更新规则' },
    })
    deleteAlertRuleMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-alert-rule-delete',
      data: null,
    })
    vi.stubGlobal('confirm', vi.fn(() => true))
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

  it('surfaces alert triage controls and filters rows before secondary rule management', async () => {
    getAlertsMock.mockResolvedValueOnce({
      success: true,
      request_id: 'req-alert-records-triage',
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
        {
          id: 11,
          symbol: '000001',
          stock_name: '平安银行',
          alert_type: 'watch',
          alert_level: 'info',
          alert_message: '观察信息，无需立即处理。',
          is_read: true,
          alert_time: '2026-04-01T09:35:00Z',
        },
      ],
    })

    const wrapper = mountAlertsPage()

    await flushPromises()

    expect(wrapper.get('[data-test="risk-alerts-triage-controls"]').text()).toContain('仅未读')
    expect(wrapper.get('[data-test="risk-alerts-triage-controls"]').text()).toContain('高优先级')
    expect(wrapper.get('[data-test="risk-alerts-table"]').text()).toContain('已跌破止损线，请立即处理。')
    expect(wrapper.get('[data-test="risk-alerts-table"]').text()).toContain('观察信息，无需立即处理。')

    await wrapper.get('[data-test="risk-alerts-filter-unread"]').trigger('click')
    expect(wrapper.get('[data-test="risk-alerts-table"]').text()).toContain('已跌破止损线，请立即处理。')
    expect(wrapper.get('[data-test="risk-alerts-table"]').text()).not.toContain('观察信息，无需立即处理。')

    await wrapper.get('[data-test="risk-alerts-filter-critical"]').trigger('click')
    expect(wrapper.get('[data-test="risk-alerts-table"]').text()).toContain('已跌破止损线，请立即处理。')
    expect(wrapper.get('[data-test="risk-alerts-rules-secondary"]').text()).toContain('规则配置')
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

  it('creates an alert rule through the canonical risk alerts page and refreshes the verified snapshot after success', async () => {
    const wrapper = mountAlertsPage()

    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('新建规则'))!.trigger('click')
    await wrapper.find('[data-test="alert-rule-name-input"]').setValue('突破放量规则')
    await wrapper.find('[data-test="alert-rule-symbol-input"]').setValue('600519')
    await wrapper.find('[data-test="alert-rule-stock-name-input"]').setValue('贵州茅台')
    await wrapper.find('[data-test="alert-rule-change-threshold-input"]').setValue('5')
    await wrapper.find('[data-test="alert-rule-volume-threshold-input"]').setValue('2')
    await wrapper.find('[data-test="alert-rule-save-button"]').trigger('click')
    await flushPromises()

    expect(createAlertRuleMock).toHaveBeenCalledWith(
      expect.objectContaining({
        rule_name: '突破放量规则',
        symbol: '600519',
        stock_name: '贵州茅台',
        rule_type: 'limit_up',
        priority: 5,
        is_active: true,
      }),
    )
    expect(createAlertRuleMock.mock.calls[0][0].parameters).toEqual(
      expect.objectContaining({
        include_st: false,
        change_percent_threshold: 5,
        volume_ratio_threshold: 2,
      }),
    )
    expect(getAlertRulesMock).toHaveBeenCalledTimes(2)
    expect(getAlertsMock).toHaveBeenCalledTimes(2)
  })

  it('keeps the last verified rules visible when an alert rule update fails', async () => {
    updateAlertRuleMock.mockResolvedValueOnce({
      success: false,
      message: 'update unavailable',
      request_id: 'req-alert-rule-update-fail',
      data: null,
    })

    const wrapper = mountAlertsPage()

    await flushPromises()

    await wrapper.find('[data-test="alert-rule-edit-1"]').trigger('click')
    await wrapper.find('[data-test="alert-rule-name-input"]').setValue('更新后的规则')
    await wrapper.find('[data-test="alert-rule-save-button"]').trigger('click')
    await flushPromises()

    expect(updateAlertRuleMock).toHaveBeenCalledWith(
      '1',
      expect.objectContaining({
        rule_name: '更新后的规则',
        symbol: '600519',
      }),
    )
    expect(getAlertRulesMock).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('单票止损线')
    expect(wrapper.text()).toContain('update unavailable')
    expect(wrapper.text()).not.toContain('req-alert-rule-update-fail')
  })

  it('deletes an alert rule only after confirmation and refreshes the canonical snapshot after success', async () => {
    const confirmMock = vi.fn(() => true)
    vi.stubGlobal('confirm', confirmMock)
    const wrapper = mountAlertsPage()

    await flushPromises()

    await wrapper.find('[data-test="alert-rule-delete-1"]').trigger('click')
    await flushPromises()

    expect(confirmMock).toHaveBeenCalledWith('确定要删除此告警规则吗？')
    expect(deleteAlertRuleMock).toHaveBeenCalledWith('1')
    expect(getAlertRulesMock).toHaveBeenCalledTimes(2)
    expect(getAlertsMock).toHaveBeenCalledTimes(2)
  })
})
