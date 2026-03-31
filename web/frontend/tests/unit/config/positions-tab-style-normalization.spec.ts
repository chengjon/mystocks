import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PositionsTab style normalization', () => {
  it('moves the table width into the existing bloomberg table class', () => {
    const source = readSource('src/views/trade-management/components/PositionsTab.vue')

    expect(source).not.toContain('style="width: 100%"')
    expect(source).toContain('.bloomberg-table {')
    expect(source).toContain('width: 100%;')
  })
})
