import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('artdeco technical analysis orphan static shell truth', () => {
  it('degrades retired ArtDeco technical analysis page without mock execution truth', () => {
    const source = readSource('src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue')

    expect(source).toContain('legacy-static-shell')
    expect(source).toContain('未接入 canonical verified truth')

    expect(source).not.toContain('GPU 核心活跃')
    expect(source).not.toContain('计算负载 12%')
    expect(source).not.toContain('Math.random')
    expect(source).not.toContain('setTimeout')
    expect(source).not.toContain('handleRunBacktest')
    expect(source).not.toContain('dashboardService')
    expect(source).not.toContain('000001.SH')
    expect(source).not.toContain('回测验证')
  })
})
