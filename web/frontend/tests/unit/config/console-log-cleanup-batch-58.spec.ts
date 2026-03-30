import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 58', () => {
  it('removes trading store placeholder logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/stores/trading.ts'), 'utf8')

    expect(source).not.toContain("console.log('Switching to function:', funcName);")
    expect(source).not.toContain("console.log('Refreshing all trading data and system status...');")
  })
})
