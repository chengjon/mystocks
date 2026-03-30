import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 39', () => {
  it('removes decision header quick action log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/trading-decision/DecisionHeader.vue'), 'utf8')

    expect(source).not.toContain("console.log('Quick action:', action)")
  })
})
