import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling Overview style source', () => {
  it('keeps Overview.vue styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/pyprofiling/components/Overview.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--gold-primary)')
    expect(source).not.toContain('var(--bg-secondary)')
    expect(source).not.toContain('rgb(212 175 55 / 30%)')
  })
})
