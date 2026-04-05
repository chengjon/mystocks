import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('trade adapters type cleanup', () => {
  it('keeps trade-adapters free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/trade-adapters.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
