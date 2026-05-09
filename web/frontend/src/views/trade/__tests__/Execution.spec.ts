import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi, beforeEach } from 'vitest'

const {
  getExecutionTrackingMock,
  getExecutionTrackingDetailMock,
  triggerExternalExecutionMock,
  routerPushMock,
} = vi.hoisted(() => ({
  getExecutionTrackingMock: vi.fn(),
  getExecutionTrackingDetailMock: vi.fn(),
  triggerExternalExecutionMock: vi.fn(),
  routerPushMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: routerPushMock }),
}))

vi.mock('@/api/trade', () => ({
  tradeApi: {
    getExecutionTracking: getExecutionTrackingMock,
    getExecutionTrackingDetail: getExecutionTrackingDetailMock,
    triggerExternalExecution: triggerExternalExecutionMock,
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

import TradeExecutionPage from '../Execution.vue'

const executionItem = {
  trackingId: 'track-101',
  accountId: 'backtest:7',
  orderId: 'backtest-7-101',
  symbol: '600519.SH',
  direction: 'buy',
  quantity: 100,
  price: 1750,
  requestedAt: '2026-05-08T09:30:00Z',
  channel: 'miniqmt',
  submissionStatus: 'bridge_task_accepted',
  brokerState: 'review_required',
  reconciliationStatus: 'not_imported',
  bridgeEvidence: {
    bridgeTaskId: 'mini-task-101',
    receiptStatus: 'accepted',
    resultStatus: 'success',
    sourceName: 'miniqmt/windows_bridge',
  },
  brokerCorrelation: {
    externalOrderId: null,
    brokerEventType: null,
    identityStatus: 'missing_broker_identity',
  },
}

describe('Trade execution tracking page', () => {
  beforeEach(() => {
    routerPushMock.mockReset()
    getExecutionTrackingMock.mockReset().mockResolvedValue({
      status: 'available',
      endpoint: 'trade',
      resource: 'execution_tracking',
      requestId: 'req-execution-list',
      verifiedAt: '2026-05-08T09:31:00Z',
      items: [executionItem],
      summary: {
        totalCount: 1,
        bridgeAcceptedCount: 1,
        brokerAcknowledgedCount: 0,
        reviewRequiredCount: 1,
        reconciledCount: 0,
      },
      totalCount: 1,
      page: 1,
      pageSize: 20,
    })
    getExecutionTrackingDetailMock.mockReset().mockResolvedValue({
      status: 'available',
      endpoint: 'trade',
      resource: 'execution_tracking_detail',
      requestId: 'req-execution-detail',
      verifiedAt: '2026-05-08T09:32:00Z',
      item: executionItem,
      evidenceTimeline: [
        { eventType: 'external_trigger_request', occurredAt: '2026-05-08T09:30:00Z', summary: '外部触发请求已记录' },
        { eventType: 'bridge_submission_receipt', occurredAt: '2026-05-08T09:30:01Z', summary: 'miniQMT bridge 已接收任务' },
      ],
    })
    triggerExternalExecutionMock.mockReset().mockResolvedValue({
      status: 'available',
      endpoint: 'trade',
      resource: 'execution_trigger',
      trackingId: 'track-new',
      accepted: true,
      submissionStatus: 'bridge_task_accepted',
      brokerState: 'review_required',
      bridgeReceipt: {
        bridgeTaskId: 'miniqmt-task-new',
        receiptStatus: 'accepted',
      },
    })
  })

  it('loads execution tracking rows and states that real trading is external', async () => {
    const wrapper = mount(TradeExecutionPage as never)

    await flushPromises()

    expect(getExecutionTrackingMock).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('执行跟踪 / 外部触发观测台')
    expect(wrapper.text()).toContain('实际交易由 miniQMT、TdxQuant 或其他外部程序完成')
    expect(wrapper.text()).toContain('600519.SH')
    expect(wrapper.text()).toContain('mini-task-101')
    expect(wrapper.text()).toContain('需复核')
  })

  it('triggers an external miniQMT request without claiming broker acknowledgement', async () => {
    const wrapper = mount(TradeExecutionPage as never)

    await flushPromises()

    await wrapper.get('[data-testid="execution-symbol-input"]').setValue('300750.SZ')
    await wrapper.get('[data-testid="execution-quantity-input"]').setValue('200')
    await wrapper.get('[data-testid="execution-price-input"]').setValue('212.5')
    await wrapper.get('[data-testid="execution-trigger-button"]').trigger('click')
    await flushPromises()

    expect(triggerExternalExecutionMock).toHaveBeenCalledWith(
      expect.objectContaining({
        channel: 'miniqmt',
        symbol: '300750.SZ',
        quantity: 200,
        price: 212.5,
      }),
    )
    expect(wrapper.text()).toContain('miniqmt-task-new')
    expect(wrapper.text()).not.toContain('券商已确认')
    expect(wrapper.text()).not.toContain('已成交')
  })

  it('opens evidence detail and jumps to reconciliation with execution context', async () => {
    const wrapper = mount(TradeExecutionPage as never)

    await flushPromises()

    await wrapper.get('[data-testid="execution-detail-track-101"]').trigger('click')
    await flushPromises()

    expect(getExecutionTrackingDetailMock).toHaveBeenCalledWith('track-101')
    expect(wrapper.text()).toContain('证据时间线')
    expect(wrapper.text()).toContain('外部触发请求已记录')

    await wrapper.get('[data-testid="execution-reconcile-track-101"]').trigger('click')

    expect(routerPushMock).toHaveBeenCalledWith({
      path: '/trade/reconciliation',
      query: {
        account_id: 'backtest:7',
        order_id: 'backtest-7-101',
        bridge_task_id: 'mini-task-101',
      },
    })
  })
})
