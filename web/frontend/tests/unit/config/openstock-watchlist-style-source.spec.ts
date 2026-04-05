import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('OpenStock WatchlistManagement style source', () => {
  it('keeps WatchlistManagement.vue on ArtDeco tokens without inline spacing literals', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/openstock/components/WatchlistManagement.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')
    expect(source).toContain('move-confirm-btn')

    expect(source).not.toContain('var(--primary)')
    expect(source).not.toContain('var(--border)')
    expect(source).not.toContain('var(--text-primary)')
    expect(source).not.toContain('margin-top: 10px')
  })
})
