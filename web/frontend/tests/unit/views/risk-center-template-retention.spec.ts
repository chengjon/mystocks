import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('risk center template retention', () => {
  it('moves the canonical risk center implementation into src/views/risk/Center.vue and keeps the ArtDeco path as a legacy wrapper', () => {
    const canonicalSource = readSource('src/views/risk/Center.vue')
    const legacySource = readSource('src/views/artdeco-pages/ArtDecoRiskManagement.vue')

    expect(canonicalSource).toContain("import ArtDecoPageTemplate from '@/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue'")
    expect(canonicalSource).toContain("import ArtDecoRiskOverviewPanel from '@/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue'")
    expect(canonicalSource).toContain("apiUrl: '/v1/trade/positions'")
    expect(legacySource).toContain("import RiskCenterCanonicalPage from '@/views/risk/Center.vue'")
    expect(legacySource).toContain('<RiskCenterCanonicalPage v-bind="attrs" />')
  })

  it('keeps the canonical risk center implementation wired to the shared ArtDecoPageTemplate', () => {
    const riskManagementSource = readSource('src/views/risk/Center.vue')

    expect(riskManagementSource).toContain("import ArtDecoPageTemplate from '@/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue'")
    expect(riskManagementSource).toContain('<ArtDecoPageTemplate')
  })

  it('retains the shared ArtDeco page template file in the active risk chain', () => {
    const templatePath = resolve(process.cwd(), 'src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue')
    const templateSource = readSource('src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue')

    expect(existsSync(templatePath)).toBe(true)
    expect(templateSource).toContain('id="artdeco-main-content"')
    expect(templateSource).toContain("name=\"content\"")
  })
})
