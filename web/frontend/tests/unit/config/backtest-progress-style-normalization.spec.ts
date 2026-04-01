import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('BacktestProgress style normalization', () => {
  it('moves result icon colors into semantic classes', () => {
    const source = readSource('src/components/sse/BacktestProgress.vue')

    expect(source).toContain('backtest-progress-icon--info')
    expect(source).toContain('backtest-progress-icon--success')
    expect(source).toContain('backtest-progress-icon--warning')
    expect(source).toContain('backtest-progress-icon--danger')
    expect(source).toContain('getResultStateClass(')

    expect(source).not.toContain(':color="getResultColor(key, value)"')
    expect(source).not.toContain('emptyIconColor')
    expect(source).not.toContain('metricPositiveColor')
    expect(source).not.toContain('metricNegativeColor')
    expect(source).not.toContain('metricWarningColor')
    expect(source).not.toContain('metricInfoColor')
  })
})
