import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('user adapter type cleanup', () => {
  it('keeps user adapter type declarations free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/user-adapters/types-1.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
