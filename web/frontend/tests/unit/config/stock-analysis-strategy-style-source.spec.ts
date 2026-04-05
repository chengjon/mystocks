import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Stock analysis Strategy style source', () => {
  it('keeps Strategy.vue styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/stock-analysis/components/Strategy.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--primary)')
    expect(source).not.toContain('var(--border)')
    expect(source).not.toContain('var(--text-primary)')
  })
})
