import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

const wrapperCases = [
  {
    label: 'system settings',
    wrapperPath: 'src/views/system/Settings.vue',
    implementationPath: 'src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue',
    importLine: "import SystemSettingsPage from '@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue'",
    renderLine: '<SystemSettingsPage v-bind="attrs" />'
  },
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
  }
] as const

describe('system wrapper retention', () => {
  for (const wrapperCase of wrapperCases) {
    it(`keeps the canonical ${wrapperCase.label} wrapper pointed at its ArtDeco implementation`, () => {
      const wrapperSource = readSource(wrapperCase.wrapperPath)
      const implementationFullPath = resolve(process.cwd(), wrapperCase.implementationPath)

      expect(existsSync(implementationFullPath)).toBe(true)
      expect(wrapperSource).toContain(wrapperCase.importLine)
      expect(wrapperSource).toContain(wrapperCase.renderLine)
    })
  }
})
