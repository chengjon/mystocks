import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FreqStrategyTab style normalization', () => {
  it('moves static section spacing and panel padding into semantic classes', () => {
    const source = readSource('src/views/freqtrade-demo/FreqStrategyTab.vue')

    expect(source).toContain('class="strategy-tabs-offset"')
    expect(source).toContain('class="strategy-indicators-panel"')
    expect(source).toContain('class="strategy-warning-alert"')
    expect(source).toContain('class="strategy-warning-list"')

    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="padding: 15px;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
  })
})
