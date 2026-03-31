import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('IndicatorPanel style normalization', () => {
  it('moves static parameter layout styling into semantic classes', () => {
    const viewSource = readSource('src/components/technical/IndicatorPanel.vue')
    const styleSource = readSource('src/components/technical/styles/IndicatorPanel.scss')

    expect(viewSource).toContain('class="toggle-indicator-icon"')
    expect(viewSource).toContain('class="config-info-alert"')
    expect(viewSource).toContain('class="param-stack"')
    expect(viewSource).toContain('class="param-input"')
    expect(viewSource).toContain('class="param-range-hint"')

    expect(viewSource).not.toContain('style="margin-right: 6px; cursor: pointer;"')
    expect(viewSource).not.toContain('style="margin-bottom: 20px;"')
    expect(viewSource).not.toContain('style="width: 100%;"')
    expect(viewSource).not.toContain('style="width: 200px;"')
    expect(viewSource).not.toContain('style="display: block; margin-top: 4px;"')

    expect(styleSource).toContain('.toggle-indicator-icon')
    expect(styleSource).toContain('.config-info-alert')
    expect(styleSource).toContain('.param-stack')
    expect(styleSource).toContain('.param-input')
    expect(styleSource).toContain('.param-range-hint')
  })
})
