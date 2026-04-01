import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PyprofilingDemo api section style normalization', () => {
  it('moves api section spacing into semantic classes', () => {
    const viewSource = readSource('src/views/PyprofilingDemo.vue')
    const styleSource = readSource('src/views/styles/PyprofilingDemo.css')
    const sectionStart = viewSource.indexOf('API STATUS')
    const sectionEnd = viewSource.indexOf('<!-- 7. 技术栈与依赖 -->')
    const apiSection = viewSource.slice(sectionStart, sectionEnd)

    expect(apiSection).toContain('class="api-status-alert"')
    expect(apiSection).toContain('class="api-section-heading-sm"')
    expect(apiSection).toContain('class="descriptions api-descriptions"')
    expect(apiSection).toContain('class="api-section-heading-lg"')
    expect(apiSection).toContain('class="api-table-offset"')
    expect(apiSection).toContain('class="api-info-alert"')
    expect(apiSection).toContain('class="api-workflow-content"')

    expect(apiSection).not.toContain('style="margin-bottom: 20px"')
    expect(apiSection).not.toContain('style="margin-top: 20px"')
    expect(apiSection).not.toContain('style="margin-top: 15px"')
    expect(apiSection).not.toContain('style="margin-top: 30px"')
    expect(apiSection).not.toContain('style="line-height: 2"')

    expect(styleSource).toContain('.api-status-alert')
    expect(styleSource).toContain('.api-workflow-content')
  })
})
