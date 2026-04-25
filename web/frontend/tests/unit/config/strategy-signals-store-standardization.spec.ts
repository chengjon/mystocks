import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const source = readFileSync(
  resolve(process.cwd(), 'src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue'),
  'utf8'
)

describe('strategy signals tab store standardization', () => {
  it('uses the standardized trading signals store instead of direct strategy API calls', () => {
    expect(source).toContain("import { useTradingSignalsStore } from '@/stores/apiStores'")
    expect(source).toContain('const tradingSignalsStore = useTradingSignalsStore()')
    expect(source).toContain('await tradingSignalsStore.refresh(params)')
    expect(source).not.toContain('strategyApi.getSignals(')
  })
})
