import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 4', () => {
  it('removes debug console.log calls from market data composable', () => {
    const source = readSource('src/composables/useMarket.ts')
    expect(source).not.toContain('console.log(')
  })
})
