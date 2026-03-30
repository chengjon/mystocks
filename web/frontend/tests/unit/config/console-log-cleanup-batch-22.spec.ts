import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 22', () => {
  it('removes market fallback compatibility init logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/marketWithFallback.ts'), 'utf8')

    expect(source).not.toContain("console.log('📊 MarketApiServiceWithFallback initialized')")
    expect(source).not.toContain("console.log('   ⚠️  This is a legacy compatibility layer')")
    expect(source).not.toContain("console.log('   ℹ️  New code should use: useMarket() composable')")
    expect(source).not.toContain('console.log(`   Real data available: ${this.useRealData}`)')
  })
})
