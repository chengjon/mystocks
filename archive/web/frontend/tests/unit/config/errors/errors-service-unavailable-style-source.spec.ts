import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('ServiceUnavailable style source', () => {
  it('keeps ServiceUnavailable styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/errors/styles/ServiceUnavailable.scss'),
      'utf8',
    )

    expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('background: var(--artdeco-bg-global);')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--bg-primary)')
    expect(source).not.toContain('var(--gold-primary)')
    expect(source).not.toContain('var(--text-muted)')
    expect(source).not.toContain('#856404')
  })
})
