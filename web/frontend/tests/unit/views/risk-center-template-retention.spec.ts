import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('risk center template retention', () => {
  it('keeps the canonical risk center wrapper pointed at ArtDecoRiskManagement', () => {
    const centerSource = readSource('src/views/risk/Center.vue')

    expect(centerSource).toContain("import RiskCenterPage from '@/views/artdeco-pages/ArtDecoRiskManagement.vue'")
    expect(centerSource).toContain('<RiskCenterPage v-bind="attrs" />')
  })

  it('keeps ArtDecoRiskManagement wired to the shared ArtDecoPageTemplate', () => {
    const riskManagementSource = readSource('src/views/artdeco-pages/ArtDecoRiskManagement.vue')

    expect(riskManagementSource).toContain("import ArtDecoPageTemplate from './_templates/ArtDecoPageTemplate.vue'")
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
