import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 40', () => {
  it('removes artdeco technical analysis stub logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue'), 'utf8')

    expect(source).not.toContain("console.log('Analyzing stock:', params)")
    expect(source).not.toContain("console.log('Running backtest task...')")
  })
})
