import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 45', () => {
  it('removes fund flow panel chart data log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/FundFlowPanel.vue'), 'utf8')

    expect(source).not.toContain("console.log('Chart data:', { dates, mainFlow, superLargeFlow, largeFlow })")
  })
})
