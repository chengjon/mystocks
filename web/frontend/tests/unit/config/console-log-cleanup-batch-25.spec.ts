import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 25', () => {
  it('removes long hu bang panel dayjs import log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/LongHuBangPanel.vue'), 'utf8')

    expect(source).not.toContain("console.log('dayjs imported in LongHuBangPanel')")
  })
})
