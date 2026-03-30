import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 41', () => {
  it('removes artdeco stock management add stock log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/ArtDecoStockManagement.vue'), 'utf8')

    expect(source).not.toContain("console.log('Opening add stock dialog...')")
  })
})
