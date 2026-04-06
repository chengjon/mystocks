import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

const wrapperCases = [
  {
    label: 'system settings',
    canonicalPath: 'src/views/system/Settings.vue',
    legacyPath: 'src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue',
    legacyImportLine: "import SystemSettingsCanonicalPage from '@/views/system/Settings.vue'",
    legacyRenderLine: '<SystemSettingsCanonicalPage v-bind="attrs" />',
    canonicalEvidence: [
      "import { monitoringApi } from '@/api'",
      "import { normalizeSystemSettingsMonitorRows, type MonitorRow } from '@/views/artdeco-pages/system-tabs/systemSettingsMonitorData.ts'",
      '系统配置中心',
      'normalizeSystemSettingsMonitorRows(detailed)',
    ]
  },
]

const compatibilityWrapperCases = [
  {
    label: 'system health',
    wrapperPath: 'src/views/system/Health.vue',
    implementationPath: 'src/views/artdeco-pages/system-tabs/SystemHealthTab.vue',
    importLine: "import SystemHealthPage from '@/views/artdeco-pages/system-tabs/SystemHealthTab.vue'",
    renderLine: '<SystemHealthPage v-bind="attrs" />'
  },
  {
    label: 'system API',
    wrapperPath: 'src/views/system/API.vue',
    implementationPath: 'src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue',
    importLine: "import SystemApiPage from '@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'",
    renderLine: '<SystemApiPage v-bind="attrs" />'
  },
  {
    label: 'system data source',
    wrapperPath: 'src/views/system/DataSource.vue',
    implementationPath: 'src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue',
    importLine: "import SystemDataSourcePage from '@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'",
    renderLine: '<SystemDataSourcePage v-bind="attrs" />'
  },
] as const

describe('system wrapper retention', () => {
  for (const wrapperCase of wrapperCases) {
    it(`moves the canonical ${wrapperCase.label} implementation into src/views/system and keeps the ArtDeco path as a legacy wrapper`, () => {
      const canonicalSource = readSource(wrapperCase.canonicalPath)
      const legacySource = readSource(wrapperCase.legacyPath)
      const legacyFullPath = resolve(process.cwd(), wrapperCase.legacyPath)

      expect(existsSync(legacyFullPath)).toBe(true)
      for (const evidenceLine of wrapperCase.canonicalEvidence) {
        expect(canonicalSource).toContain(evidenceLine)
      }
      expect(legacySource).toContain(wrapperCase.legacyImportLine)
      expect(legacySource).toContain(wrapperCase.legacyRenderLine)
    })
  }

  for (const wrapperCase of compatibilityWrapperCases) {
    it(`keeps the canonical ${wrapperCase.label} wrapper pointed at its ArtDeco implementation`, () => {
      const wrapperSource = readSource(wrapperCase.wrapperPath)
      const implementationFullPath = resolve(process.cwd(), wrapperCase.implementationPath)

      expect(existsSync(implementationFullPath)).toBe(true)
      expect(wrapperSource).toContain(wrapperCase.importLine)
      expect(wrapperSource).toContain(wrapperCase.renderLine)
    })
  }
})
