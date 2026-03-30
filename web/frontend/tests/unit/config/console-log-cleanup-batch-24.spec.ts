import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 24', () => {
  it('removes data visualization showcase chart ready log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/DataVisualizationShowcase.vue'), 'utf8')

    expect(source).not.toContain('console.log(`${chartType} chart ready:`, instance)')
  })
})
