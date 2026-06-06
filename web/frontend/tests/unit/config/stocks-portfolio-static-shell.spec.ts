import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('stocks portfolio orphan static shell truth', () => {
  it('degrades the retired stocks portfolio child page without mock portfolio execution truth', () => {
    const source = readSource('src/views/stocks/Portfolio.vue')

    expect(source).toContain('legacy-static-shell')
    expect(source).toContain('未接入 canonical verified truth')

    expect(source).not.toContain('PORTFOLIO MANAGEMENT')
    expect(source).not.toContain('portfolioMetrics')
    expect(source).not.toContain('positions = ref')
    expect(source).not.toContain('Math.random')
    expect(source).not.toContain('ElMessage')
    expect(source).not.toContain('ADD POSITION')
    expect(source).not.toContain('Portfolio refreshed')
    expect(source).not.toContain('000001')
    expect(source).not.toContain('平安银行')
    expect(source).not.toContain('performancePeriod')
  })
})
