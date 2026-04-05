import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Converted archive dashboard style source', () => {
  it('keeps dashboard.vue on modern ArtDeco tokens', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/converted.archive/dashboard.vue'),
      'utf8',
    )

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain("@import '@/styles/artdeco-tokens';")
    expect(source).not.toContain('var(--artdeco-up)')
    expect(source).not.toContain('var(--artdeco-danger)')
    expect(source).not.toContain('var(--artdeco-font-accent)')
    expect(source).not.toContain('height: 300px')
    expect(source).not.toContain('width: 200px')
    expect(source).not.toContain('width: 40px')
    expect(source).not.toContain('rgb(212 175 55 / 5%)')
  })
})
