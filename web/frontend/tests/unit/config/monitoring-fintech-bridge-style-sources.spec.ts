import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('monitoring fintech bridge style sources', () => {
  it('bridges legacy fintech variables onto ArtDeco tokens', () => {
    const files = [
      'src/views/monitoring/styles/RiskDashboard.scss',
      'src/views/monitoring/styles/WatchlistManagement.scss',
    ]

    for (const file of files) {
      const source = readSource(file)

      expect(source).toContain('background: var(--artdeco-bg-global);')
      expect(source).toContain('--fintech-space-1: var(--artdeco-spacing-1);')
      expect(source).toContain('--fintech-bg-primary: var(--artdeco-bg-global);')
      expect(source).toContain('--fintech-accent-primary: var(--artdeco-gold-primary);')
      expect(source).toContain('--fintech-font-family-ui: var(--artdeco-font-body, var(--font-body));')
    }
  })
})
