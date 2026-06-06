import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('risk orphan page static shell truth', () => {
  it('degrades retired risk child pages without phase-roadmap placeholder truth', () => {
    const portfolio = readSource('src/views/risk/Portfolio.vue')
    const positions = readSource('src/views/risk/Positions.vue')

    for (const source of [portfolio, positions]) {
      expect(source).toContain('legacy-static-shell')
      expect(source).toContain('未接入 canonical verified truth')
      expect(source).not.toContain('Coming Soon')
      expect(source).not.toContain('Phase 7')
      expect(source).not.toContain('el-alert')
    }

    expect(portfolio).not.toContain('Portfolio Risk Analysis')
    expect(positions).not.toContain('Position Risk Analysis')
  })
})
