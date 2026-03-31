import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('Phase4Dashboard style normalization', () => {
  it('moves static stat icon gradients and warning text color into local classes', () => {
    const source = readSource('src/views/Phase4Dashboard.vue')

    expect(source).toContain('phase4-stat-icon-market')
    expect(source).toContain('phase4-stat-icon-watchlist')
    expect(source).toContain('phase4-stat-icon-portfolio')
    expect(source).toContain('phase4-stat-icon-risk')
    expect(source).toContain('phase4-stat-value-warning')

    expect(source).not.toContain('style="background: linear-gradient(45deg, var(--gold-primary), #E5C158);"')
    expect(source).not.toContain('style="background: linear-gradient(45deg, var(--fall), #69F0AE);"')
    expect(source).not.toContain('style="background: linear-gradient(45deg, var(--warning), #FFD54F);"')
    expect(source).not.toContain('style="background: linear-gradient(45deg, var(--rise), #FF8A80);"')
    expect(source).not.toContain('style="color: var(--warning);"')
  })
})
