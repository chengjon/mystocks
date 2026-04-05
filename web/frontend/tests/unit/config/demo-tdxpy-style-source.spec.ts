import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Demo Tdxpy style source', () => {
  it('keeps TdxpyDemo.scss on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/demo/styles/TdxpyDemo.scss'), 'utf8')

    expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--accent-gold)')
    expect(source).not.toContain('var(--spacing-')
    expect(source).not.toContain("font-family: 'Courier New'")
  })
})
