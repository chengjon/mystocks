import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import ArtDecoRiskOverviewPanel from '../ArtDecoRiskOverviewPanel.vue'
import {
  concentrationMetrics,
  createInitialRiskAlerts,
  sectorDistribution,
  type RiskAlertItem,
} from '../riskManagementHelpers'

const mountRiskOverviewPanel = (
  riskAlerts: RiskAlertItem[] = createInitialRiskAlerts(),
  panelProps: Record<string, unknown> = {},
) =>
  mount(ArtDecoRiskOverviewPanel as never, {
    props: {
      riskAlerts,
      sectorDistribution,
      concentrationMetrics,
      ...panelProps,
    },
    global: {
      stubs: {
        ArtDecoCard: {
          template: `
            <section class="artdeco-card-stub">
              <div class="card-header"><slot name="header" /></div>
              <div class="card-body"><slot /></div>
            </section>
          `,
        },
        ArtDecoBadge: {
          props: ['variant'],
          template: '<span class="artdeco-badge-stub"><slot /></span>',
        },
        ArtDecoButton: {
          emits: ['click'],
          template: '<button class="artdeco-button-stub" @click="$emit(\'click\', $event)"><slot /></button>',
        },
      },
    },
  })

describe('ArtDecoRiskOverviewPanel', () => {
  let riskAlerts: RiskAlertItem[]

  beforeEach(() => {
    riskAlerts = createInitialRiskAlerts()
  })

  it('renders the three primary domain sections', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)

    expect(wrapper.text()).toContain('行业持仓分布')
    expect(wrapper.text()).toContain('仓位集中度分析')
    expect(wrapper.text()).toContain('风险预警列表')
  })

  it('keeps tab panel accessibility semantics on the root container', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)
    const root = wrapper.get('#risk-panel-overview')

    expect(root.attributes('role')).toBe('tabpanel')
    expect(root.attributes('aria-labelledby')).toBe('risk-tab-overview')
  })

  it('renders risk alert rows and stock identity information', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)
    const rows = wrapper.findAll('tbody tr')

    expect(rows).toHaveLength(riskAlerts.length)
    expect(wrapper.text()).toContain('平安银行')
    expect(wrapper.text()).toContain('000001.SZ')
  })

  it('shows the alert count badge only when alerts are present', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)

    expect(wrapper.text()).toContain(`${riskAlerts.length} 条预警`)

    const emptyWrapper = mountRiskOverviewPanel([])
    expect(emptyWrapper.text()).not.toContain('条预警')
  })

  it('keeps the risk table structure even when alerts are empty', () => {
    const wrapper = mountRiskOverviewPanel([])

    expect(wrapper.text()).toContain('风险预警列表')
    expect(wrapper.findAll('tbody tr')).toHaveLength(0)
    expect(wrapper.find('table.risk-table').exists()).toBe(true)
  })

  it('maps risk level and stop status labels into Chinese domain copy', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)

    expect(wrapper.text()).toContain('高风险')
    expect(wrapper.text()).toContain('中风险')
    expect(wrapper.text()).toContain('低风险')
    expect(wrapper.text()).toContain('已触发')
    expect(wrapper.text()).toContain('接近')
    expect(wrapper.text()).toContain('正常')
  })

  it('renders action text from the current alert row', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)

    expect(wrapper.text()).toContain('减仓')
    expect(wrapper.text()).toContain('监控')
    expect(wrapper.text()).toContain('止损')
    expect(wrapper.text()).toContain('持有')
  })

  it('emits the selected RiskAlertItem when an action button is clicked', async () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)
    const actionButtons = wrapper.findAll('.artdeco-button-stub')

    await actionButtons[0]!.trigger('click')

    expect(wrapper.emitted('action')).toEqual([[riskAlerts[0]]])
  })

  it('degrades holdings-derived rows into observation mode when policy inputs are unavailable', () => {
    const wrapper = mountRiskOverviewPanel([
      {
        code: '600519.SH',
        name: '贵州茅台',
        riskLevel: 'high',
        position: 54.36,
        stopStatus: 'unverified',
        action: '待复核',
        policyReady: false,
      },
      {
        code: '300750.SZ',
        name: '宁德时代',
        riskLevel: 'medium',
        position: 45.64,
        stopStatus: 'unverified',
        action: '待复核',
        policyReady: false,
      },
    ], {
      sectorDistribution: [],
      concentrationMetrics: [],
    })

    expect(wrapper.text()).toContain('风险观察列表')
    expect(wrapper.text()).toContain('2 条观察项')
    expect(wrapper.text()).toContain('当前仅基于真实持仓暴露生成风险观察项，未接入止损/减仓策略参数。')
    expect(wrapper.text()).toContain('策略状态')
    expect(wrapper.text()).toContain('复核状态')
    expect(wrapper.text()).toContain('未校验')
    expect(wrapper.text()).toContain('待复核')
    expect(wrapper.text()).not.toContain('风险预警列表')
  })

  it('renders static sector distribution and concentration metrics sections', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)

    expect(wrapper.text()).toContain('科技股')
    expect(wrapper.text()).toContain('医药生物')
    expect(wrapper.text()).toContain('前10大重仓股占比')
    expect(wrapper.text()).toContain('65 / 70')
  })

  it('shows pending integration states instead of static overview placeholders when live sector and concentration data are unavailable', () => {
    const wrapper = mountRiskOverviewPanel([], {
      sectorDistribution: [],
      concentrationMetrics: [],
    })

    expect(wrapper.text()).toContain('行业分布待接入')
    expect(wrapper.text()).toContain('集中度指标待接入')
    expect(wrapper.text()).not.toContain('科技股')
    expect(wrapper.text()).not.toContain('医药生物')
    expect(wrapper.text()).not.toContain('前10大重仓股占比')
    expect(wrapper.text()).not.toContain('65 / 70')
  })

  it('attaches domain state classes for risk level and stop status tags', () => {
    const wrapper = mountRiskOverviewPanel(riskAlerts)

    const highRiskBadge = wrapper.find('.risk-badge.high')
    const approachingStatus = wrapper.find('.stop-status.approaching')
    const triggeredStatus = wrapper.find('.stop-status.triggered')

    expect(highRiskBadge.exists()).toBe(true)
    expect(approachingStatus.exists()).toBe(true)
    expect(triggeredStatus.exists()).toBe(true)
  })
})
