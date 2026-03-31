import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FreqOverviewTab style normalization', () => {
  it('moves static section spacing and resource list styles into semantic classes', () => {
    const source = readSource('src/views/freqtrade-demo/FreqOverviewTab.vue')

    expect(source).toContain('class="section-heading-spaced"')
    expect(source).toContain('class="resource-list"')
    expect(source).toContain('.section-heading-spaced {')
    expect(source).toContain('.resource-list {')

    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 10px; line-height: 1.8;"')
  })
})
