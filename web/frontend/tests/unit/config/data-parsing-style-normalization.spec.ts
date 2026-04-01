import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('DataParsing style normalization', () => {
  it('moves static table spacing into a semantic class', () => {
    const source = readSource('src/views/demo/stock-analysis/components/DataParsing.vue')

    expect(source).toContain('class="table data-table-offset"')
    expect(source).toContain('.data-table-offset {')
    expect(source).not.toContain('style="margin-top: 15px;"')
  })
})
