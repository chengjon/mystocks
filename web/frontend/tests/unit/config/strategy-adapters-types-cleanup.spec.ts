import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('strategy adapters type cleanup', () => {
  it('keeps strategy-adapters free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/strategy-adapters.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
