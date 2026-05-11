import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Forbidden error page style source', () => {
  it('keeps Forbidden styles on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/errors/Forbidden.vue'), 'utf8')

    expect(source).toContain('var(--artdeco-bg-global)')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--bg-primary)')
    expect(source).not.toContain('var(--gold-primary)')
    expect(source).not.toContain('var(--text-muted)')
    expect(source).not.toContain('rgb(212 175 55 / 2%)')
  })
})
