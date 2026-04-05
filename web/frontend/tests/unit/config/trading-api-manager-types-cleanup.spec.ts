import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('TradingApiManager type cleanup', () => {
  it('keeps TradingApiManager free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/services/TradingApiManager.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
