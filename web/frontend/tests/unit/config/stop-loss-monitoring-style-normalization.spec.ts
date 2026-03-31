import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('StopLossMonitoringTab style normalization', () => {
  it('moves static inline widths and offsets into semantic classes', () => {
    const viewSource = readSource('src/views/components/StopLossMonitoringTab.vue')
    const styleSource = readSource('src/views/components/styles/StopLossMonitoringTab.css')

    expect(viewSource).toContain('class="monitoring-table"')
    expect(viewSource).toContain('class="position-form-control"')
    expect(viewSource).toContain('class="action-button-spaced"')

    expect(viewSource).not.toContain('style="width: 100%"')
    expect(viewSource).not.toContain('style="width: 100%;"')
    expect(viewSource).not.toContain('style="margin-left: 8px;"')

    expect(styleSource).toContain('.monitoring-table')
    expect(styleSource).toContain('.position-form-control')
    expect(styleSource).toContain('.action-button-spaced')
  })
})
