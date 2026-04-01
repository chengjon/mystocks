import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('Pyprofiling Profiling style normalization', () => {
  it('moves static section spacing into semantic classes', () => {
    const source = readSource('src/views/demo/pyprofiling/components/Profiling.vue')

    expect(source).toContain('class="table profiling-table-offset"')
    expect(source).toContain('class="profiling-section-heading"')
    expect(source).toContain('.profiling-table-offset {')
    expect(source).toContain('.profiling-section-heading {')

    expect(source).not.toContain('style="margin-top: 15px"')
    expect(source).not.toContain('style="margin-top: 30px"')
  })
})
