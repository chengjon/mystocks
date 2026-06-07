import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 28', () => {
  it('keeps the archived stock detail shell free of k-line loaded logs', () => {
    const source = readFileSync(
      resolve(process.cwd(), '../../archive/web/frontend/src/views/root-legacy/stock-detail/StockDetail.vue'),
      'utf8',
    )

    expect(source).not.toContain("console.log('K-line data loaded:', data.length, 'records')")
  })
})
