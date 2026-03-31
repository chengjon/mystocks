import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('MarketFundFlow style normalization', () => {
  it('moves static gradient stop styling into semantic classes', () => {
    const source = readSource('src/views/artdeco-pages/components/MarketFundFlow.vue')

    expect(source).toContain('class="fund-positive-start"')
    expect(source).toContain('class="fund-positive-end"')
    expect(source).toContain('class="fund-negative-start"')
    expect(source).toContain('class="fund-negative-end"')

    expect(source).not.toContain('style="stop-color: var(--artdeco-up); stop-opacity: 60%"')
    expect(source).not.toContain('style="stop-color: var(--artdeco-up); stop-opacity: 10%"')
    expect(source).not.toContain('style="stop-color: var(--artdeco-down); stop-opacity: 60%"')
    expect(source).not.toContain('style="stop-color: var(--artdeco-down); stop-opacity: 10%"')

    expect(source).toContain('.fund-positive-start')
    expect(source).toContain('.fund-negative-end')
  })
})
