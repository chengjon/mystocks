import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Converted archive backtest style source', () => {
  it('keeps backtest-management.vue on modern ArtDeco tokens', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/converted.archive/backtest-management.vue'),
      'utf8',
    )

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain("@import '@/styles/artdeco-tokens';")
    expect(source).not.toContain('var(--artdeco-danger)')
    expect(source).not.toContain('var(--artdeco-fg-secondary)')
    expect(source).not.toContain('280px')
    expect(source).not.toContain('200px')
    expect(source).not.toContain('300px')
    expect(source).not.toContain('1200px')
  })
})
