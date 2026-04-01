import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('NestedMenu style source', () => {
  it('keeps default menu colors on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/layout/NestedMenu.vue'), 'utf8')

    expect(source).toContain("default: 'var(--artdeco-bg-base)'")
    expect(source).toContain("default: 'var(--artdeco-fg-muted)'")
    expect(source).toContain("default: 'var(--artdeco-gold-primary)'")

    expect(source).not.toContain("default: '#304156'")
    expect(source).not.toContain("default: '#bfcbd9'")
    expect(source).not.toContain("default: '#409EFF'")
  })
})
