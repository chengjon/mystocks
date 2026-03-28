import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('monitoring/system/strategy page style normalization', () => {
  it('normalizes page style entrypoints onto @use', () => {
    const files = [
      'src/views/monitoring/AlertRulesManagement.vue',
      'src/views/monitoring/MonitoringDashboard.vue',
      'src/views/monitoring/RiskDashboard.vue',
      'src/views/monitoring/WatchlistManagement.vue',
      'src/views/system/Architecture.vue',
      'src/views/system/DatabaseMonitor.vue',
      'src/views/system/PerformanceMonitor.vue',
      'src/views/strategy/BacktestGPU.vue',
      'src/views/strategy/BatchScan.vue',
      'src/views/strategy/ResultsQuery.vue',
      'src/views/strategy/SingleRun.vue',
      'src/views/strategy/StatsAnalysis.vue',
      'src/views/strategy/StrategyList.vue',
      'src/views/trade-management/components/TradeHistoryTab.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).toContain('@use')
      expect(source).not.toContain('@import "./styles/')
    }
  })
})
