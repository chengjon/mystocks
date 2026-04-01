import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('Data Concepts style normalization', () => {
  it('moves trend bar color variants into semantic classes', () => {
    const source = readSource('src/views/data/Concepts.vue')

    expect(source).toContain("'trend-bar'")
    expect(source).toContain("'trend-bar--rise'")
    expect(source).toContain("'trend-bar--down'")

    expect(source).not.toContain(":style=\"{ height: `${Math.abs(c.change_pct) * 5}px`, background: c.change_pct >= 0 ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }\"")
    expect(source).toContain('.trend-bar--rise')
    expect(source).toContain('.trend-bar--down')
  })
})
