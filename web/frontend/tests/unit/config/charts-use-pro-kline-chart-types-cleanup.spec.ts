import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('charts useProKLineChart type cleanup', () => {
  it('keeps the charts kline composable free of ts-nocheck', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/components/charts/composables/useProKLineChart.ts'),
      'utf8'
    )
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
