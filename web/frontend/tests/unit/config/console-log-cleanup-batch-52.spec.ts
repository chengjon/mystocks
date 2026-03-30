import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 52', () => {
  it('removes strategy builder mounted log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/quant/StrategyBuilder.vue'), 'utf8')

    expect(source).not.toContain("console.log('StrategyBuilder组件已挂载')")
  })
})
