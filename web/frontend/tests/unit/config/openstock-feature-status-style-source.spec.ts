import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('OpenStock FeatureStatus style source', () => {
  it('keeps FeatureStatus.vue styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/openstock/components/FeatureStatus.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--warning)')
    expect(source).not.toContain('var(--border-light)')
    expect(source).not.toContain('var(--text-primary)')
  })
})
