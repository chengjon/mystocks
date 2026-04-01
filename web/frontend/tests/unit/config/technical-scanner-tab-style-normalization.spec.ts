import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TechnicalScannerTab style normalization', () => {
  it('moves trend gauge color variants into semantic classes', () => {
    const viewSource = readSource('src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue')

    expect(viewSource).toContain("'gauge-fill'")
    expect(viewSource).toContain("'gauge-fill--rise'")
    expect(viewSource).toContain("'gauge-fill--down'")

    expect(viewSource).not.toContain(":style=\"{ width: `${Number(stock.trend_score) * 10}%`, background: stock.macd_signal === 'BULL' ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }\"")
    expect(viewSource).toContain(".gauge-fill--rise")
    expect(viewSource).toContain(".gauge-fill--down")
  })
})
