import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('useMarket source hygiene', () => {
  it('does not keep stale market overview merge TODO blocks after the real API bridges landed', () => {
    const source = readSource('src/composables/useMarket.ts')

    expect(source).not.toContain("TODO: MarketOverviewVM interface doesn't have chipRaces field")
    expect(source).not.toContain("TODO: MarketOverviewVM interface doesn't have longHuBang field")
    expect(source).not.toContain('vm.chipRaces = MarketAdapter.adaptChipRace')
    expect(source).not.toContain('vm.longHuBang = MarketAdapter.adaptLongHuBang')
  })
})
