import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Network error page style source', () => {
  it('keeps NetworkError styles on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/errors/NetworkError.vue'), 'utf8')

    expect(source).toContain('var(--artdeco-bg-global)')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--bg-primary)')
    expect(source).not.toContain('var(--gold-primary)')
    expect(source).not.toContain('var(--text-muted)')
    expect(source).not.toContain('#f56c6c')
  })
})
