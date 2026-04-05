import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('indicators-extended functions-2 type cleanup', () => {
  it('keeps indicators-extended/functions-2 free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/indicators-extended/functions-2.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
