import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling Tech style source', () => {
  it('keeps Tech.vue styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/pyprofiling/components/Tech.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain("font-family: 'SF Mono'")
    expect(source).not.toContain('var(--primary)')
    expect(source).not.toContain('var(--bg-dark)')
  })
})
