import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('WatchlistGroupManager style normalization', () => {
  it('moves group palette colors onto theme variables', () => {
    const source = readSource('src/components/watchlist/WatchlistGroupManager.vue')

    expect(source).toContain('var(--color-border-light)')
    expect(source).toContain('var(--color-text-primary)')
    expect(source).toContain('var(--color-bg-primary)')
    expect(source).toContain('var(--color-border)')
    expect(source).toContain('var(--color-bg-secondary)')
    expect(source).toContain('var(--color-info)')
    expect(source).toContain('color-mix(in srgb, var(--color-info) 10%, transparent)')

    expect(source).not.toContain('#eee')
    expect(source).not.toContain('#333')
    expect(source).not.toContain('#fff')
    expect(source).not.toContain('#e0e0e0')
    expect(source).not.toContain('#f5f7fa')
    expect(source).not.toContain('#ecf5ff')
    expect(source).not.toContain('#409eff')
  })
})
