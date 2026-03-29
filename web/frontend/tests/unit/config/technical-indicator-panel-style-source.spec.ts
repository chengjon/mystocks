import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('IndicatorPanel style source', () => {
  it('keeps IndicatorPanel styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/components/technical/styles/IndicatorPanel.scss'),
      'utf8',
    )

    expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('#f5f7fa')
    expect(source).not.toContain('#303133')
    expect(source).not.toContain('#409eff')
    expect(source).not.toContain('#ebeef5')
  })
})
