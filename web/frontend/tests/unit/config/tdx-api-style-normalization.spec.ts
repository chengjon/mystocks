import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TdxApiTab style normalization', () => {
  it('moves static collapse and table spacing into semantic classes', () => {
    const source = readSource('src/views/tdxpy-demo/TdxApiTab.vue')

    expect(source).toContain('class="api-collapse-offset"')
    expect(source).toContain('class="api-subsection-heading"')
    expect(source).toContain('class="api-table-offset"')

    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="margin-top: 15px;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
  })
})
