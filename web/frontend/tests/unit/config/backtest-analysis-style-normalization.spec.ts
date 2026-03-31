import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('BacktestAnalysis style normalization', () => {
  it('moves repeated section spacing and table width into semantic classes', () => {
    const viewSource = readSource('src/views/BacktestAnalysis.vue')
    const styleSource = readSource('src/views/styles/BacktestAnalysis.css')

    expect(viewSource).toContain('class="section-offset"')
    expect(viewSource).toContain('class="trade-history-table"')
    expect(viewSource).toContain('class="chart-placeholder"')

    expect(viewSource).not.toContain('style="margin-top: 20px;"')
    expect(viewSource).not.toContain('style="width: 100%"')
    expect(viewSource).not.toContain('style="text-align: center; padding: 40px; color: #666;"')

    expect(styleSource).toContain('.section-offset')
    expect(styleSource).toContain('.trade-history-table')
    expect(styleSource).toContain('.chart-placeholder')
  })
})
