import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('user adapter runtime cleanup', () => {
  it('keeps user-adapters/part-2 free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/user-adapters/part-2.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
