import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('indicators-extended part-1 type cleanup', () => {
  it('keeps indicators-extended/part-1 free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/indicators-extended/part-1.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
