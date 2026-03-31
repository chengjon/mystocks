import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TdxExportTab style normalization', () => {
  it('moves the tabs top spacing into a semantic class', () => {
    const source = readSource('src/views/tdxpy-demo/TdxExportTab.vue')

    expect(source).toContain('class="export-tabs-offset"')
    expect(source).toContain('.export-tabs-offset {')
    expect(source).not.toContain('style="margin-top: 20px;"')
  })
})
