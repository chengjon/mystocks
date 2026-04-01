import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PyprofilingDemo features section style normalization', () => {
  it('moves feature-engineering section spacing into semantic classes', () => {
    const viewSource = readSource('src/views/PyprofilingDemo.vue')
    const styleSource = readSource('src/views/styles/PyprofilingDemo.css')
    const sectionStart = viewSource.indexOf('ROLLING WINDOW FEATURE GENERATION')
    const sectionEnd = viewSource.indexOf('<!-- 4. 性能分析工具 -->')
    const featuresSection = viewSource.slice(sectionStart, sectionEnd)

    expect(featuresSection).toContain('class="descriptions page-features-descriptions"')
    expect(featuresSection).toContain('class="page-section-heading-spaced"')
    expect(featuresSection).toContain('class="page-table-offset"')
    expect(featuresSection).toContain('class="page-alert-offset-sm"')

    expect(featuresSection).not.toContain('<el-descriptions :column="1" border style="margin-top: 15px" class="descriptions">')
    expect(featuresSection).not.toContain('<h3 style="margin-top: 30px">FEATURE SELECTION ALGORITHMS</h3>')
    expect(featuresSection).not.toContain('<el-table :data="featureSelectionMethods" style="margin-top: 15px">')
    expect(featuresSection).not.toContain('<el-alert type="warning" :closable="false" style="margin-top: 15px">')

    expect(styleSource).toContain('.page-features-descriptions')
    expect(styleSource).toContain('.page-section-heading-spaced')
    expect(styleSource).toContain('.page-table-offset')
    expect(styleSource).toContain('.page-alert-offset-sm')
  })
})
