import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const archiveFiles = [
  'src/views/converted.archive/data-analysis.vue',
  'src/views/converted.archive/risk-management.vue',
  'src/views/converted.archive/stock-management.vue',
]

describe('Converted archive shared style template', () => {
  it('keeps small converted archive pages on the ArtDeco @use template', () => {
    const sources = archiveFiles.map((file) => readFileSync(resolve(process.cwd(), file), 'utf8'))

    for (const source of sources) {
      expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
      expect(source).toContain('var(--artdeco-bg-global)')
      expect(source).toContain('var(--artdeco-gold-primary)')
      expect(source).not.toContain("@import '@/styles/artdeco-tokens';")
      expect(source).not.toContain('height: 300px')
      expect(source).not.toContain('border-radius: 8px')
      expect(source).not.toContain('height: 2px')
    }
  })
})
