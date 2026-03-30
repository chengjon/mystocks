import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 36', () => {
  it('removes decision positions stub action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/trading-decision/DecisionPositions.vue'), 'utf8')

    expect(source).not.toContain("console.log('Quick buy:', stock.code)")
    expect(source).not.toContain("console.log('Quick sell:', stock.code)")
    expect(source).not.toContain("console.log('Refresh positions')")
  })
})
