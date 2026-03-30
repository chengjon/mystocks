import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 34', () => {
  it('removes artdeco data analysis selection logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/artdeco-pages/ArtDecoDataAnalysis.vue'), 'utf8')

    expect(source).not.toContain("console.log('Selected:', ind.name)")
    expect(source).not.toContain("console.log('Clicked:', row.symbol)")
  })
})
