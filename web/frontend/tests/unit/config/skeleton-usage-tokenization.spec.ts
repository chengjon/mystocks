import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('ArtDecoSkeleton tokenization', () => {
  it('keeps skeleton component sizing on design-token expressions', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/artdeco/core/ArtDecoSkeleton.vue'), 'utf8')

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain("return 'var(--artdeco-spacing-1)'")
    expect(source).toContain("return 'var(--artdeco-spacing-2)'")
    expect(source).toContain('height: var(--artdeco-spacing-4);')
    expect(source).toContain('margin-bottom: var(--artdeco-spacing-2);')

    expect(source).not.toContain("@import '@/styles/artdeco-tokens")
    expect(source).not.toContain("return '4px'")
    expect(source).not.toContain("return '8px'")
    expect(source).not.toContain("return '2px'")
    expect(source).not.toContain('height: 1em;')
    expect(source).not.toContain('margin-bottom: 0.5em;')
  })
})
