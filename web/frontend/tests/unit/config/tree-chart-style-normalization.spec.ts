import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TreeChart style normalization', () => {
  it('moves static layout selector width into a semantic class', () => {
    const source = readSource('src/components/Charts/TreeChart.vue')

    expect(source).toContain('class="tree-layout-select"')
    expect(source).toContain('.tree-layout-select {')
    expect(source).not.toContain('style="width: 120px"')
  })
})
