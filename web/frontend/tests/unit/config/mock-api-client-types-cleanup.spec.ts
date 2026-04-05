import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('mock api client type cleanup', () => {
  it('keeps the mock api client free of ts-nocheck', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/mockApiClient.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
