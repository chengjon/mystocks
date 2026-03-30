import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 30', () => {
  it('removes portfolio performance chart update log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/stocks/Portfolio.vue'), 'utf8')

    expect(source).not.toContain("console.log('Update performance chart for period:', performancePeriod.value)")
  })
})
