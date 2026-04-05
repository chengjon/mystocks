import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Demo Phase4Dashboard entry style source', () => {
  it('keeps Phase4Dashboard.vue free of inline stat icon gradients', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/demo/Phase4Dashboard.vue'), 'utf8')

    expect(source).toContain('market-indices-icon')
    expect(source).toContain('watchlist-icon')
    expect(source).toContain('portfolio-icon')
    expect(source).toContain('risk-alerts-icon')

    expect(source).not.toContain('style="background: linear-gradient')
    expect(source).not.toContain('var(--accent-gold)')
    expect(source).not.toContain('#27AE60')
    expect(source).not.toContain('#E67E22')
    expect(source).not.toContain('#E74C3C')
  })
})
