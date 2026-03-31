import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TdxStatusTab style normalization', () => {
  it('moves static section spacing into semantic classes', () => {
    const source = readSource('src/views/tdxpy-demo/TdxStatusTab.vue')

    expect(source).toContain('class="status-descriptions"')
    expect(source).toContain('class="status-section-heading"')
    expect(source).toContain('class="status-timeline"')
    expect(source).toContain('class="status-row"')
    expect(source).toContain('class="status-alert"')
    expect(source).toContain('class="status-alert-list"')

    expect(source).not.toContain('style="margin-top: 15px;"')
    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
  })
})
