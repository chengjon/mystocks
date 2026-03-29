import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('StockSearchBar style source', () => {
  it('keeps StockSearchBar styles on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/technical/StockSearchBar.vue'), 'utf8')

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('#303133')
    expect(source).not.toContain('#606266')
    expect(source).not.toContain('width: 400px')
  })
})
