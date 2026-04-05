import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('oscillator type cleanup', () => {
  it('keeps the oscillator barrel free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/indicator/oscillator.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
