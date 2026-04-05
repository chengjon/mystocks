import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('OpenStockDemo style source', () => {
  it('keeps OpenStockDemo styles on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/demo/OpenStockDemo.vue'), 'utf8')

    expect(source).toContain('var(--artdeco-bg-global)')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('#E67E22')
    expect(source).not.toContain('var(--accent-gold)')
    expect(source).not.toContain('var(--spacing-')
  })
})
