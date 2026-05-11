import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('root/demo style entrypoints', () => {
  it('keeps view entrypoints on @use', () => {
    const viewFiles = [
      'src/views/Analysis.vue',
      'src/views/BacktestAnalysis.vue',
      'src/views/BacktestWizard.vue',
      'src/views/Dashboard.vue',
      'src/views/DataVisualizationShowcase.vue',
      'src/views/EnhancedDashboard.vue',
      'src/views/IndicatorLibrary.vue',
      'src/views/IndustryConceptAnalysis.vue',
      'src/views/Phase4Dashboard.vue',
      'src/views/PortfolioManagement.vue',
      'src/views/PyprofilingDemo.vue',
      'src/views/RealTimeMonitor.vue',
      'src/views/Settings.vue',
      'src/views/StockAnalysisDemo.vue',
      'src/views/StockDetail.vue',
      'src/views/StrategyManagement.vue',
      'src/views/TaskManagement.vue',
      'src/views/TradingDashboard.vue',
      'src/views/demo/Phase4Dashboard.vue',
      'src/views/demo/pyprofiling/components/Prediction.vue',
    ]

    for (const file of viewFiles) {
      const source = readSource(file)
      expect(source).toContain('@use')
      expect(source).not.toContain('@import "./styles/')
      expect(source).not.toContain("@import './styles/")
    }
  })

  it('keeps shared style sources on @use token imports', () => {
    const styleFiles = [
      'src/views/styles/Analysis.scss',
      'src/views/styles/BacktestWizard.scss',
      'src/views/styles/Dashboard.scss',
      'src/views/styles/IndustryConceptAnalysis.scss',
      'src/views/styles/Settings.scss',
      'src/views/styles/TradingDecisionCenter.scss',
    ]

    for (const file of styleFiles) {
      const source = readSource(file)
      expect(source).toContain('@use')
      expect(source).not.toContain("@import '@/styles/")
      expect(source).not.toContain("@import \"@/styles/")
    }
  })
})
