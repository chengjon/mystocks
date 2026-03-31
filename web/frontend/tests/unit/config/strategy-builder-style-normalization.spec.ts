import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('StrategyBuilder style normalization', () => {
  it('moves static result layout sizing into semantic classes', () => {
    const source = readSource('src/components/quant/StrategyBuilder.vue')

    expect(source).toContain('class="results-card strategy-results-offset"')
    expect(source).toContain('class="strategy-trades-table"')
    expect(source).toContain('class="strategy-chart-container"')

    expect(source).toContain('.strategy-results-offset {')
    expect(source).toContain('.strategy-trades-table {')
    expect(source).toContain('.strategy-chart-container {')

    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="width: 100%"')
    expect(source).not.toContain('style="width: 100%; height: 500px;"')
  })
})
