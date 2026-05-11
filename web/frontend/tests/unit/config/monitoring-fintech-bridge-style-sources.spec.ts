import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('monitoring fintech bridge style sources', () => {
  it('keeps legacy fintech bridge guards off archived monitoring styles', () => {
    const source = readSource('src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue')

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).not.toContain('styles/WatchlistManagement.scss')
  })
})
