import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TechnicalAnalysis style normalization', () => {
  it('moves static input and select widths into semantic classes', () => {
    const viewSource = readSource('src/views/technical/TechnicalAnalysis.vue')
    const styleSource = readSource('src/views/technical/styles/TechnicalAnalysis.scss')

    expect(viewSource).toContain('class="technical-symbol-input"')
    expect(viewSource).toContain('class="technical-indicators-select"')
    expect(viewSource).toContain('class="technical-batch-symbols-input"')

    expect(viewSource).not.toContain('style="width: 180px"')
    expect(viewSource).not.toContain('style="width: 320px"')
    expect(viewSource).not.toContain('style="width: 440px"')

    expect(styleSource).toContain('.technical-symbol-input')
    expect(styleSource).toContain('.technical-indicators-select')
    expect(styleSource).toContain('.technical-batch-symbols-input')
  })
})
