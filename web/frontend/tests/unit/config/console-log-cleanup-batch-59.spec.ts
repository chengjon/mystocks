import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 59', () => {
  it('removes artdeco trading data placeholder logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/artdeco/useTradingData.ts'), 'utf8')

    expect(source).not.toContain("console.log('Refreshing trading data...')")
    expect(source).not.toContain("console.log('Searching history:', {")
  })
})
