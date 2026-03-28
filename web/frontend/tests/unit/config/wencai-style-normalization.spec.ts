import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('wencai style normalization', () => {
  it('keeps Wencai entrypoints on @use and design tokens', () => {
    const queryTable = readSource('src/components/market/WencaiQueryTable.vue')
    const testPage = readSource('src/components/market/WencaiTest.vue')
    const demoPage = readSource('src/views/demo/Wencai.vue')
    const marketStyle = readSource('src/views/styles/Market.scss')

    expect(queryTable).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(queryTable).not.toContain('color: #333')
    expect(queryTable).not.toContain('background: #f5f7fa')

    expect(testPage).toContain('<style scoped lang="scss">')
    expect(testPage).toContain('var(--artdeco-gold-primary)')

    expect(demoPage).toContain('@use "./styles/Wencai.scss" as *;')
    expect(demoPage).not.toContain('@import "./styles/Wencai"')

    expect(marketStyle).toContain("@use '@/styles/theme-tokens.scss' as *;")
    expect(marketStyle).not.toContain("@import '@/styles/theme-tokens';")
  })
})
