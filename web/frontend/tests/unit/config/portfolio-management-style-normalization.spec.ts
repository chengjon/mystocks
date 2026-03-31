import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PortfolioManagement style normalization', () => {
  it('moves static dialog form widths into a shared semantic class', () => {
    const viewSource = readSource('src/views/PortfolioManagement.vue')
    const styleSource = readSource('src/views/styles/PortfolioManagement.scss')

    expect(viewSource).toContain('class="portfolio-form-control"')
    expect(viewSource).not.toContain('style="width: 100%"')

    expect(styleSource).toContain('.portfolio-form-control')
    expect(styleSource).toContain('width: 100%')
  })
})
