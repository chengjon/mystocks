import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('strategy dialog type cleanup', () => {
  it('keeps the strategy dialog free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/StrategyDialog.vue'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
