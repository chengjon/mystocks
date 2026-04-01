import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FundFlowPanel tooltip style normalization', () => {
  it('moves tooltip line colors into dedicated classes', () => {
    const source = readSource('src/components/market/FundFlowPanel.vue')

    expect(source).toContain('fund-flow-tooltip-positive')
    expect(source).toContain('fund-flow-tooltip-negative')
    expect(source).not.toContain('<span style="color: ${color}">')
    expect(source).toContain('.fund-flow-tooltip-positive')
    expect(source).toContain('.fund-flow-tooltip-negative')
  })
})
