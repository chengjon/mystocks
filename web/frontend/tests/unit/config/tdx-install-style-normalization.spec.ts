import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TdxInstallTab style normalization', () => {
  it('moves static install page spacing into semantic classes', () => {
    const source = readSource('src/views/tdxpy-demo/TdxInstallTab.vue')

    expect(source).toContain('class="install-section-heading"')
    expect(source).toContain('class="install-tabs-offset"')
    expect(source).toContain('class="install-subsection-heading"')
    expect(source).toContain('class="install-table-offset"')
    expect(source).toContain('class="install-info-alert"')

    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="margin-top: 20px;"')
    expect(source).not.toContain('style="margin-top: 10px;"')
    expect(source).not.toContain('style="margin-top: 15px;"')
  })
})
