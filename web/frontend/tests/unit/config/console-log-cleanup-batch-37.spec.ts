import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 37', () => {
  it('removes decision orders stub action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/trading-decision/DecisionOrders.vue'), 'utf8')

    expect(source).not.toContain("console.log('Quick action:', action)")
    expect(source).not.toContain("console.log('Quick buy:', orderForm)")
    expect(source).not.toContain("console.log('Quick sell:', orderForm)")
    expect(source).not.toContain("console.log('Refresh orders')")
  })
})
