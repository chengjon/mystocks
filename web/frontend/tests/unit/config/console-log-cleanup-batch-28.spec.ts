import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 28', () => {
  it('removes stock detail k-line loaded log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/StockDetail.vue'), 'utf8')

    expect(source).not.toContain("console.log('K-line data loaded:', data.length, 'records')")
  })
})
