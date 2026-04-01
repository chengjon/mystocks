import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('LongHuBangTable style normalization', () => {
  it('moves trend icon color onto semantic amount classes', () => {
    const source = readSource('src/components/market/LongHuBangTable.vue')

    expect(source).toContain('getTrendIconClass(totalNetAmount)')
    expect(source).toContain("return value > 0 ? 'amount-positive' : 'amount-negative'")
    expect(source).not.toContain(':color="getTrendIconColor(totalNetAmount)"')
    expect(source).not.toContain('getTrendIconColor')
  })
})
