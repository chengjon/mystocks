import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('auto-import declarations type cleanup', () => {
  it('keeps auto-import declarations free of TS suppression directives', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/auto-imports.d.ts'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'
    const tsIgnoreDirective = '@ts-' + 'ignore'

    expect(source).not.toContain(tsNoCheckDirective)
    expect(source).not.toContain(tsIgnoreDirective)
  })
})
