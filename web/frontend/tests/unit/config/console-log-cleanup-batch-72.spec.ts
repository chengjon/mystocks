import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 72', () => {
  it('removes stock detail trading summary fallback info log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/StockDetail.vue'), 'utf8')

    expect(source).not.toContain("console.info('Trading summary API not implemented, using mock data for:', symbol)")
  })
})
