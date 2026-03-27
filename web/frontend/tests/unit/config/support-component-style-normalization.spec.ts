import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('support component style normalization', () => {
  it('normalizes data action button onto artdeco tokens', () => {
    const source = readSource('src/components/data/ActionButton.vue')

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).not.toContain('background: #1A1A1A;')
  })

  it('normalizes data table header styling onto artdeco tokens', () => {
    const source = readSource('src/components/data/DataTable.vue')

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).not.toContain('background: #141414;')
  })

  it('normalizes monitoring stat card sizing through semantic variables', () => {
    const source = readSource('src/components/monitoring/MonitoringStatCard.vue')

    expect(source).toContain('--monitoring-stat-lift:')
    expect(source).toContain('var(--monitoring-stat-icon-size)')
    expect(source).not.toContain('transform: translateY(-2px);')
  })

  it('normalizes realtime panel palette onto fintech variables', () => {
    const source = readSource('src/components/realtime/styles/RealtimePositionPanel.scss')

    expect(source).toContain('var(--fintech-gray-1)')
    expect(source).toContain('--realtime-position-panel-success-tint:')
    expect(source).not.toContain('background: #fff;')
  })

  it('normalizes shared chart container theme accessors', () => {
    const source = readSource('src/components/shared/charts/ChartContainer.vue')

    expect(source).toContain('const tooltipTheme =')
    expect(source).toContain('const axisLineTheme =')
  })

  it('normalizes sse cards onto artdeco tokens', () => {
    const riskAlertsSource = readSource('src/components/sse/RiskAlerts.vue')
    const trainingSource = readSource('src/components/sse/TrainingProgress.vue')

    expect(riskAlertsSource).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(trainingSource).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
  })

  it('normalizes legacy view support css onto theme variables', () => {
    const source = readSource('src/views/components/styles/RiskOverviewTab.css')

    expect(source).toContain('var(--color-stock-down)')
    expect(source).not.toContain('#67C23A')
  })
})
