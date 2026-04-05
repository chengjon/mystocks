import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Converted archive trading-management style source', () => {
  it('keeps trading-management.vue on the modern ArtDeco token grid', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/converted.archive/trading-management.vue'),
      'utf8',
    )

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain(
      'grid-template-columns: calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-10)) minmax(0, 1fr);',
    )
    expect(source).toContain('color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent)')

    expect(source).not.toContain("@import '@/styles/artdeco-tokens';")
    expect(source).not.toContain('@include artdeco-layout')
    expect(source).not.toContain('@include artdeco-content-spacing')
    expect(source).not.toContain('var(--artdeco-danger)')
    expect(source).not.toContain('280px')
    expect(source).not.toContain('200px')
    expect(source).not.toContain('border-radius: 4px')
    expect(source).not.toContain('rgb(212 175 55 / 20%)')
  })
})
