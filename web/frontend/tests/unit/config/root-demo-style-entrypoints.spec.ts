import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('root/demo style entrypoints', () => {
  it('keeps view entrypoints free of deprecated style imports', () => {
    const viewFiles = [
      'src/views/Analysis.vue',
      'src/views/BacktestAnalysis.vue',
      'src/views/BacktestWizard.vue',
      'src/views/Dashboard.vue',
      'src/views/EnhancedDashboard.vue',
      'src/views/IndicatorLibrary.vue',
      'src/views/Phase4Dashboard.vue',
      'src/views/PyprofilingDemo.vue',
      'src/views/RealTimeMonitor.vue',
      'src/views/Settings.vue',
      'src/views/StockDetail.vue',
      'src/views/StrategyManagement.vue',
      'src/views/TradingDashboard.vue',
      'src/views/demo/Phase4Dashboard.vue',
      'src/views/demo/pyprofiling/components/Prediction.vue',
    ]

    for (const file of viewFiles) {
      const source = readSource(file)
      expect(source).not.toContain('@import "./styles/')
      expect(source).not.toContain("@import './styles/")
    }
  })

  it('keeps shared style sources on @use token imports', () => {
    const styleFiles = [
      'src/views/styles/Analysis.scss',
      'src/views/styles/Dashboard.scss',
      'src/views/styles/Settings.scss',
      'src/views/styles/TradingDecisionCenter.scss',
    ]

    for (const file of styleFiles) {
      expect(existsSync(resolve(process.cwd(), file))).toBe(true)
      const source = readSource(file)
      expect(source).toContain('@use')
      expect(source).not.toContain("@import '@/styles/")
      expect(source).not.toContain("@import \"@/styles/")
    }
  })
})
