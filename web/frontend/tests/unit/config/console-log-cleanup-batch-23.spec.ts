import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 23', () => {
  it('removes technical analysis mounted log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/technical/composables/useTechnicalAnalysis.ts'), 'utf8')

    expect(source).not.toContain("console.log('Technical Analysis page mounted')")
  })
})
