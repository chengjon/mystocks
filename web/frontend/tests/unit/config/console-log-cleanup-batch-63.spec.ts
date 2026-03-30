import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 63', () => {
  it('removes kline api debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/klineApi.ts'), 'utf8')

    expect(source).not.toContain('console.log(`[KLINE API] ${config.method?.toUpperCase()} ${config.url} [${timestamp}]`);')
    expect(source).not.toContain("console.log('[KLINE API] Cache hit:', cacheKey);")
    expect(source).not.toContain("console.log('[KLINE API] Cache cleared');")
  })
})
