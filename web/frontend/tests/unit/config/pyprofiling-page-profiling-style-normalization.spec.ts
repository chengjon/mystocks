import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PyprofilingDemo profiling section style normalization', () => {
  it('moves profiling section spacing into semantic classes', () => {
    const viewSource = readSource('src/views/PyprofilingDemo.vue')
    const styleSource = readSource('src/views/styles/PyprofilingDemo.css')
    const sectionStart = viewSource.indexOf('PERFORMANCE ANALYSIS TOOLS COMPARISON')
    const sectionEnd = viewSource.indexOf('<!-- 5. 数据文件说明 -->')
    const profilingSection = viewSource.slice(sectionStart, sectionEnd)

    expect(profilingSection).toContain('class="profiling-table-offset"')
    expect(profilingSection).toContain('class="profiling-section-heading"')
    expect(profilingSection).toContain('class="command-desc profiling-command-note"')
    expect(profilingSection).toContain('class="profiling-alert-offset"')
    expect(profilingSection).toContain('class="profiling-workflow-content"')

    expect(profilingSection).not.toContain('style="margin-top: 15px"')
    expect(profilingSection).not.toContain('style="margin-top: 30px"')
    expect(profilingSection).not.toContain('style="margin-top: 10px; color: var(--fg-muted); font-size: 13px"')
    expect(profilingSection).not.toContain('style="margin-top: 20px"')
    expect(profilingSection).not.toContain('style="line-height: 2"')

    expect(styleSource).toContain('.profiling-table-offset')
    expect(styleSource).toContain('.profiling-command-note')
    expect(styleSource).toContain('.profiling-workflow-content')
  })
})
