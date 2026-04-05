import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

const wrapperCases = [
  {
    label: 'risk overview',
    canonicalPath: 'src/views/risk/Overview.vue',
    legacyPath: 'src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue',
    legacyImportLine: "import RiskOverviewCanonicalPage from '@/views/risk/Overview.vue'",
    legacyRenderLine: '<RiskOverviewCanonicalPage v-bind="attrs" />',
    canonicalEvidence: [
      "import { monitoringApi } from '@/api/index'",
      'title="风险概览工作台"',
      'monitoringApi.getAlertRules()',
    ],
  },
  {
    label: 'risk stop-loss',
    wrapperPath: 'src/views/risk/StopLoss.vue',
    implementationPath: 'src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue',
    importLine: "import RiskStopLossPage from '@/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue'",
    renderLine: '<RiskStopLossPage v-bind="attrs" />',
  },
  {
    label: 'risk alerts',
    wrapperPath: 'src/views/risk/Alerts.vue',
    implementationPath: 'src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue',
    importLine: "import RiskAlertsPage from '@/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue'",
    renderLine: '<RiskAlertsPage v-bind="attrs" />',
  },
  {
    label: 'risk news',
    wrapperPath: 'src/views/risk/News.vue',
    implementationPath: 'src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue',
    importLine: "import RiskNewsPage from '@/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue'",
    renderLine: '<RiskNewsPage v-bind="attrs" />',
  },
] as const

describe('risk wrapper retention', () => {
  it('moves the canonical risk overview implementation into src/views/risk/Overview.vue and keeps the ArtDeco path as a legacy wrapper', () => {
    const canonicalSource = readSource(wrapperCases[0].canonicalPath)
    const legacySource = readSource(wrapperCases[0].legacyPath)
    const legacyFullPath = resolve(process.cwd(), wrapperCases[0].legacyPath)

    expect(existsSync(legacyFullPath)).toBe(true)
    for (const evidenceLine of wrapperCases[0].canonicalEvidence) {
      expect(canonicalSource).toContain(evidenceLine)
    }
    expect(legacySource).toContain(wrapperCases[0].legacyImportLine)
    expect(legacySource).toContain(wrapperCases[0].legacyRenderLine)
  })

  for (const wrapperCase of wrapperCases.slice(1)) {
    it(`keeps the canonical ${wrapperCase.label} wrapper pointed at its ArtDeco implementation`, () => {
      const wrapperSource = readSource(wrapperCase.wrapperPath)
      const implementationFullPath = resolve(process.cwd(), wrapperCase.implementationPath)

      expect(existsSync(implementationFullPath)).toBe(true)
      expect(wrapperSource).toContain(wrapperCase.importLine)
      expect(wrapperSource).toContain(wrapperCase.renderLine)
    })
  }
})
