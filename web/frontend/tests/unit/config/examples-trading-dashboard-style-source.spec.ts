import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Examples TradingDashboard style source', () => {
  it('keeps TradingDashboard.migrated.vue on ArtDeco tokens', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/examples/TradingDashboard.migrated.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('padding: 20px')
    expect(source).not.toContain('#f5f7fa')
    expect(source).not.toContain('#606266')
  })
})
