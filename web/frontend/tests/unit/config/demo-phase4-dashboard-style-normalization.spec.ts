import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('Demo Phase4Dashboard style normalization', () => {
  it('moves static stat icon gradients into local classes', () => {
    const source = readSource('src/views/demo/Phase4Dashboard.vue')

    expect(source).toContain('demo-phase4-stat-icon-market')
    expect(source).toContain('demo-phase4-stat-icon-watchlist')
    expect(source).toContain('demo-phase4-stat-icon-portfolio')
    expect(source).toContain('demo-phase4-stat-icon-risk')

    expect(source).not.toContain('style="background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-light))"')
    expect(source).not.toContain('style="background: linear-gradient(135deg, #27AE60, #2ECC71)"')
    expect(source).not.toContain('style="background: linear-gradient(135deg, #E67E22, #F39C12)"')
    expect(source).not.toContain('style="background: linear-gradient(135deg, #E74C3C, #C0392B)"')
  })
})
