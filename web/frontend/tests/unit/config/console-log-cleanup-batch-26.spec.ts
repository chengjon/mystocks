import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 26', () => {
  it('removes wencai panel mounted log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/WencaiPanelSimple.vue'), 'utf8')

    expect(source).not.toContain("console.log('WencaiPanelSimple mounted')")
  })
})
