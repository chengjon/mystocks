import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('legacy useTechnicalAnalysis type cleanup', () => {
  it('keeps the legacy technical analysis composable free of ts-nocheck', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/composables/useTechnicalAnalysis.ts'),
      'utf8'
    )
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
