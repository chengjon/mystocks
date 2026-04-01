import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PyprofilingDemo data section style normalization', () => {
  it('moves data section spacing into semantic classes', () => {
    const viewSource = readSource('src/views/PyprofilingDemo.vue')
    const styleSource = readSource('src/views/styles/PyprofilingDemo.css')
    const sectionStart = viewSource.indexOf('项目数据文件')
    const sectionEnd = viewSource.indexOf('<!-- 6. API 服务 -->')
    const dataSection = viewSource.slice(sectionStart, sectionEnd)

    expect(dataSection).toContain('class="data-table-offset"')
    expect(dataSection).toContain('class="data-section-heading"')
    expect(dataSection).toContain('class="data-descriptions"')
    expect(dataSection).toContain('class="data-alert-offset"')
    expect(dataSection).toContain('class="data-workflow-content"')

    expect(dataSection).not.toContain('style="margin-top: 15px"')
    expect(dataSection).not.toContain('style="margin-top: 30px"')
    expect(dataSection).not.toContain('style="margin-top: 20px"')
    expect(dataSection).not.toContain('style="line-height: 2"')

    expect(styleSource).toContain('.data-table-offset')
    expect(styleSource).toContain('.data-workflow-content')
  })
})
