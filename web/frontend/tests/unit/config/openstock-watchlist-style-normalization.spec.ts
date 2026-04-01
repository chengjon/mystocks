import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('OpenStock WatchlistManagement style normalization', () => {
  it('moves the move-stock button spacing into a semantic class', () => {
    const source = readSource('src/views/demo/openstock/components/WatchlistManagement.vue')

    expect(source).toContain('class="move-stock-btn"')
    expect(source).toContain('.move-stock-btn {')
    expect(source).not.toContain('style="width: 100%; margin-top: 10px;"')
  })
})
