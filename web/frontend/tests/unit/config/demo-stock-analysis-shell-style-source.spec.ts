import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Demo StockAnalysis shell style source', () => {
  it('keeps StockAnalysisDemo.vue shell styles on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/demo/StockAnalysisDemo.vue'), 'utf8')

    expect(source).toContain('var(--artdeco-bg-global)')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--gold-primary)')
    expect(source).not.toContain('var(--spacing-')
    expect(source).not.toContain('rgb(212 175 55 / 2%)')
  })
})
