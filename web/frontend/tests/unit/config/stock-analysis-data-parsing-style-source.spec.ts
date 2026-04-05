import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Stock analysis DataParsing style source', () => {
  it('keeps DataParsing.vue styles on ArtDeco token variables without inline spacing literals', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/stock-analysis/components/DataParsing.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')
    expect(source).toContain('class="table table-spacing"')

    expect(source).not.toContain('var(--primary)')
    expect(source).not.toContain('var(--border)')
    expect(source).not.toContain('var(--text-primary)')
    expect(source).not.toContain('margin-top: 15px')
  })
})
