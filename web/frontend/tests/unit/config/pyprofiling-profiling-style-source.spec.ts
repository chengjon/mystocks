import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling Profiling style source', () => {
  it('keeps Profiling.vue styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/demo/pyprofiling/components/Profiling.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('rgb(39 174 96 / 15%)')
    expect(source).not.toContain('#27AE60')
    expect(source).not.toContain('var(--accent-gold)')
  })
})
