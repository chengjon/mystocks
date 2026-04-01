import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('OpenStock demo tokenization hygiene', () => {
  it('moves selected OpenStock demo panels onto the ArtDeco token vocabulary', () => {
    const files = [
      'src/views/demo/openstock/components/FeatureStatus.vue',
      'src/views/demo/openstock/components/KlineChart.vue',
      'src/views/demo/openstock/components/StockNews.vue',
      'src/views/demo/openstock/components/StockQuote.vue',
    ]

    for (const file of files) {
      const source = readSource(file)

      expect(source).toContain("@use '../../../../styles/artdeco-tokens.scss' as *;")
      expect(source).not.toContain('var(--bg-primary)')
      expect(source).not.toContain('var(--bg-secondary)')
      expect(source).not.toContain('var(--text-primary)')
      expect(source).not.toContain('var(--text-secondary)')
      expect(source).not.toContain('var(--border)')
      expect(source).not.toContain('var(--border-light)')
      expect(source).not.toContain('var(--radius-sm)')
      expect(source).not.toContain('var(--radius-md)')
      expect(source).not.toContain('var(--primary)')
    }
  })
})
