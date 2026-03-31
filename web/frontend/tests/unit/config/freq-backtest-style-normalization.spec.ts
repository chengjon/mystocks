import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FreqBacktestTab style normalization', () => {
  it('moves static section spacing into semantic classes', () => {
    const source = readSource('src/views/freqtrade-demo/FreqBacktestTab.vue')

    expect(source).toContain('class="backtest-steps"')
    expect(source).toContain('class="backtest-section-heading"')
    expect(source).toContain('class="backtest-tabs"')
    expect(source).toContain('class="backtest-metrics-table"')
    expect(source).toContain('class="backtest-info-alert"')
    expect(source).toContain('class="backtest-info-list"')

    expect(source).not.toContain('style="margin: 30px 0;"')
    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="margin-top: 15px;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
  })
})
