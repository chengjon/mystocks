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
    const composableSource = readSource('src/views/composables/usePortfolioManagement.ts')

    expect(viewSource).toContain('class="portfolio-form-control"')
    expect(viewSource).toContain('portfolio-stat--info')
    expect(viewSource).toContain('portfolio-stat--danger')
    expect(viewSource).toContain('portfolio-stat--warning')
    expect(viewSource).toContain('portfolio-stat--success')
    expect(viewSource).toContain('getHealthStateClass(')
    expect(viewSource).toContain('getRiskStateClass(')
    expect(viewSource).toContain('getAlertStateClass()')
    expect(viewSource).not.toContain('style="width: 100%"')
    expect(viewSource).not.toContain(':style="{ color: getHealthColor(portfolioSummary.total_score) }"')
    expect(viewSource).not.toContain(':style="{ color: getRiskColor(portfolioSummary.risk_score) }"')
    expect(viewSource).not.toContain(':style="{ color: getAlertColor() }"')
    expect(viewSource).not.toContain('color="#409EFF"')
    expect(viewSource).not.toContain('color="#F56C6C"')
    expect(viewSource).not.toContain('color="#E6A23C"')
    expect(viewSource).not.toContain('color="#67C23A"')

    expect(styleSource).toContain('.portfolio-form-control')
    expect(styleSource).toContain('width: 100%')
    expect(styleSource).toContain('.portfolio-stat--neutral')
    expect(styleSource).toContain('.portfolio-stat--info')
    expect(styleSource).toContain('.portfolio-stat--success')
    expect(styleSource).toContain('.portfolio-stat--warning')
    expect(styleSource).toContain('.portfolio-stat--danger')

    expect(composableSource).toContain('const getHealthStateClass')
    expect(composableSource).toContain('const getRiskStateClass')
    expect(composableSource).toContain('const getAlertStateClass')
    expect(composableSource).toContain("return 'var(--color-success)'")
    expect(composableSource).toContain("return 'var(--color-warning)'")
    expect(composableSource).toContain("return 'var(--color-danger)'")
    expect(composableSource).not.toContain('const getHealthColor')
    expect(composableSource).not.toContain('const getRiskColor')
    expect(composableSource).not.toContain('const getAlertColor')
    expect(composableSource).not.toContain("return '#67C23A'")
    expect(composableSource).not.toContain("return '#E6A23C'")
    expect(composableSource).not.toContain("return '#F56C6C'")
  })
})
