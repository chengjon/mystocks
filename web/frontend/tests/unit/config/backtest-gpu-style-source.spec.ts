import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('BacktestGPU style source', () => {
  it('keeps BacktestGPU styles on ArtDeco tokens', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/strategy/styles/BacktestGPU.scss'),
      'utf8',
    )

    expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-bg-card)')
    expect(source).toContain('var(--artdeco-fg-primary)')

    expect(source).not.toContain('var(--color-')
    expect(source).not.toContain('var(--spacing-')
    expect(source).not.toContain('var(--font-size-')
    expect(source).not.toContain('var(--border-radius-')
  })
})
