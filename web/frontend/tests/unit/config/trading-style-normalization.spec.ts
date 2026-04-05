import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const tradingFiles = [
  'src/views/trading/Execution.vue',
  'src/views/trading/History.vue',
  'src/views/trading/Orders.vue',
  'src/views/trading/Positions.vue',
]

describe('Trading style normalization', () => {
  it('keeps placeholder trading views on ArtDeco spacing tokens', () => {
    const sources = tradingFiles.map((file) => readFileSync(resolve(process.cwd(), file), 'utf8'))

    for (const source of sources) {
      expect(source).toContain('var(--artdeco-spacing-5)')
      expect(source).not.toContain('padding: 20px')
    }
  })
})
