import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FreqConfigTab style normalization', () => {
  it('moves static section spacing into semantic classes', () => {
    const source = readSource('src/views/freqtrade-demo/FreqConfigTab.vue')

    expect(source).toContain('class="config-tabs-offset"')
    expect(source).toContain('class="config-section-heading"')
    expect(source).toContain('class="config-descriptions"')
    expect(source).toContain('.config-tabs-offset {')
    expect(source).toContain('.config-descriptions {')

    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 15px;"')
  })
})
