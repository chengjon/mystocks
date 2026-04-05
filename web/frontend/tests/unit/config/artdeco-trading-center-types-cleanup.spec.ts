import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('ArtDecoTradingCenter type cleanup', () => {
  it('keeps ArtDecoTradingCenter free of TS suppression directives', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/ArtDecoTradingCenter.vue'), 'utf8')
    const tsNoCheckDirective = '@ts-' + 'nocheck'
    const tsIgnoreDirective = '@ts-' + 'ignore'
    const tsExpectErrorDirective = '@ts-' + 'expect-error'

    expect(source).not.toContain(tsNoCheckDirective)
    expect(source).not.toContain(tsIgnoreDirective)
    expect(source).not.toContain(tsExpectErrorDirective)
  })
})
