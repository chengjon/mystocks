import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('style cleanup batch 79', () => {
  it('removes static full-width inline style from fund flow table', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/FundFlowPanel.vue'), 'utf8')

    expect(source).not.toContain('style="width: 100%"')
  })
})
