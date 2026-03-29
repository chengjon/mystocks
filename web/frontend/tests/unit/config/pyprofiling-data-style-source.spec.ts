import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling Data style source', () => {
  it('keeps Data.vue styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/pyprofiling/components/Data.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('rgb(212 175 55 / 10%)')
    expect(source).not.toContain('var(--accent-gold)')
    expect(source).not.toContain('var(--fg-secondary)')
  })
})
