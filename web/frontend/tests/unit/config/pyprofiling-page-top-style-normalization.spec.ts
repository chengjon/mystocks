import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PyprofilingDemo top section style normalization', () => {
  it('moves early-page static spacing and config styles into semantic classes', () => {
    const viewSource = readSource('src/views/PyprofilingDemo.vue')
    const styleSource = readSource('src/views/styles/PyprofilingDemo.css')

    expect(viewSource).toContain('class="overview-features-block"')
    expect(viewSource).toContain('class="config-box"')
    expect(viewSource).toContain('class="config-box-list"')
    expect(viewSource).toContain('class="steps profiling-steps"')
    expect(viewSource).toContain('class="model-results"')
    expect(viewSource).toContain('class="model-results-alert"')

    expect(viewSource).not.toContain('<div style="margin-top: 20px">')
    expect(viewSource).not.toContain('style="background: var(--bg-secondary); padding: 15px; border-radius: 4px; margin-bottom: 20px;"')
    expect(viewSource).not.toContain('style="margin: 20px 0"')

    expect(styleSource).toContain('.overview-features-block')
    expect(styleSource).toContain('.config-box')
    expect(styleSource).toContain('.model-results-alert')
  })
})
