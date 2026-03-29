import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('KLineChart style source', () => {
  it('keeps KLineChart styles on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/technical/KLineChart.vue'), 'utf8')

    expect(source).toContain('var(--artdeco-bg-global)')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')
    expect(source).toContain('class="indicator-toggle-icon"')
    expect(source).toContain('.indicator-toggle-icon')

    expect(source).not.toContain('background: #fff')
    expect(source).not.toContain('#909399')
    expect(source).not.toContain('#e4e7ed')
    expect(source).not.toContain('#f5f7fa')
  })
})
