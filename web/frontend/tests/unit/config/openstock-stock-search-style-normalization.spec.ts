import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('OpenStock StockSearch style normalization', () => {
  it('moves the add-to-watchlist button spacing into a semantic class', () => {
    const source = readSource('src/views/demo/openstock/components/StockSearch.vue')

    expect(source).toContain('class="watchlist-submit-btn"')
    expect(source).toContain('.watchlist-submit-btn {')
    expect(source).not.toContain('style="width: 100%; margin-top: 12px;"')
  })
})
