import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 68', () => {
  it('removes market adapter mock fallback logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/adapters/marketAdapter.ts'), 'utf8')

    expect(source).not.toContain("console.log('[MarketAdapter] 📦 Using Mock Market Overview data');")
    expect(source).not.toContain("console.log('[MarketAdapter] 📦 Using Mock Fund Flow data');")
    expect(source).not.toContain("console.log('[MarketAdapter] 📦 Using Mock K-Line data');")
  })
})
