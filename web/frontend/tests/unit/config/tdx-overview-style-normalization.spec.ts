import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TdxOverviewTab style normalization', () => {
  it('moves static section spacing and title styling into semantic classes', () => {
    const source = readSource('src/views/tdxpy-demo/TdxOverviewTab.vue')

    expect(source).toContain('class="overview-section-heading"')
    expect(source).toContain('class="overview-descriptions descriptions"')
    expect(source).toContain('class="overview-resource-alert"')
    expect(source).toContain('class="overview-resource-title"')
    expect(source).toContain('class="overview-resource-list"')

    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 15px;"')
    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="font-weight: bold;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
  })
})
