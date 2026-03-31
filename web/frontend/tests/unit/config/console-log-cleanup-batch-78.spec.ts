import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('style cleanup batch 78', () => {
  it('removes static full-width inline styles from market data tables', () => {
    const files = [
      'src/components/market/LongHuBangTable.vue',
      'src/components/market/ChipRaceTable.vue',
      'src/components/market/ETFDataTable.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('style="width: 100%"')
    }
  })
})
