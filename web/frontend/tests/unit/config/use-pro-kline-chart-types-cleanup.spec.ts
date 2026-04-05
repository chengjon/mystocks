import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('useProKLineChart type cleanup', () => {
  it('keeps the market kline composable free of TS suppression directives', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/components/market/composables/useProKLineChart.ts'),
      'utf8'
    )
    const tsNoCheckDirective = '@ts-' + 'nocheck'
    const tsIgnoreDirective = '@ts-' + 'ignore'

    expect(source).not.toContain(tsNoCheckDirective)
    expect(source).not.toContain(tsIgnoreDirective)
  })
})
