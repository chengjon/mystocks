import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('indicator selector type cleanup', () => {
  it('keeps the market indicator selector free of TS suppression directives', () => {
    const tsNoCheckDirective = '@ts-' + 'nocheck'
    const tsExpectErrorDirective = '@ts-' + 'expect-error'
    const files = [
      'src/components/market/IndicatorSelector.vue',
      'src/components/Charts/IndicatorSelector.vue',
    ]

    for (const file of files) {
      const source = readFileSync(resolve(process.cwd(), file), 'utf8')

      expect(source).not.toContain(tsNoCheckDirective)
      expect(source).not.toContain(tsExpectErrorDirective)
    }
  })
})
