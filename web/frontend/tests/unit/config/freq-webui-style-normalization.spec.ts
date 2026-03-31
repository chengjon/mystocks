import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FreqWebuiTab style normalization', () => {
  it('moves static section spacing into semantic classes', () => {
    const source = readSource('src/views/freqtrade-demo/FreqWebuiTab.vue')

    expect(source).toContain('class="webui-feature-grid"')
    expect(source).toContain('class="webui-section-heading"')
    expect(source).toContain('class="webui-info-alert"')
    expect(source).toContain('class="webui-info-note"')
    expect(source).toContain('class="webui-link-row"')
    expect(source).toContain('class="webui-api-table"')

    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
    expect(source).not.toContain('style="margin-top: 15px;"')
  })
})
