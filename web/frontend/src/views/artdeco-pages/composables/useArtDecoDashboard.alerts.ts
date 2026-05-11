import type { DashboardAlertItem } from './useArtDecoDashboard.types.ts'

type DashboardAlertInput = {
  marketError?: string
  fundFlowError?: string
  industryError?: string
  fundFlowDegradedMessage?: string
  industryDegradedMessage?: string
}

export function buildDashboardAlertItems(input: DashboardAlertInput): DashboardAlertItem[] {
  const alerts: DashboardAlertItem[] = []

  if (input.marketError) {
    alerts.push({
      id: 'market-failed',
      severity: 'failed',
      label: 'FAILED',
      message: input.marketError,
      action: '核心行情未同步，等待下次刷新。'
    })
  }

  if (input.fundFlowError) {
    alerts.push({
      id: 'fund-flow-failed',
      severity: 'failed',
      label: 'FAILED',
      message: input.fundFlowError,
      action: '资金流向无可用快照，暂不执行压力测试。'
    })
  } else if (input.fundFlowDegradedMessage) {
    alerts.push({
      id: 'fund-flow-degraded',
      severity: 'degraded',
      label: 'DEGRADED',
      message: input.fundFlowDegradedMessage,
      action: '当前仍显示上次成功同步的资金快照。'
    })
  }

  if (input.industryError) {
    alerts.push({
      id: 'industry-failed',
      severity: 'failed',
      label: 'FAILED',
      message: input.industryError,
      action: '行业热度无可用快照，相关图表已暂停。'
    })
  } else if (input.industryDegradedMessage) {
    alerts.push({
      id: 'industry-degraded',
      severity: 'degraded',
      label: 'DEGRADED',
      message: input.industryDegradedMessage,
      action: '当前仍显示上次成功同步的行业热度。'
    })
  }

  return alerts
}
