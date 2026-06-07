import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('TradeManagement style entrypoint', () => {
  it('delegates TradeManagement to the canonical ArtDeco page without stale local styles', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/TradeManagement.vue'), 'utf8')

    expect(source).toContain("import ArtDecoTradingManagementPage from '@/views/artdeco-pages/ArtDecoTradingManagement.vue'")
    expect(source).toContain('<ArtDecoTradingManagementPage v-bind="attrs" />')
    expect(source).not.toContain('<style')
    expect(source).not.toContain("@import '@/styles/theme-tokens';")
  })
})
