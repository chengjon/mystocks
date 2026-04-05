import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Converted archive market-data style source', () => {
  it('keeps market-data.vue and market-data.scss on modern ArtDeco tokens', () => {
    const vueSource = readFileSync(
      resolve(process.cwd(), 'src/views/converted.archive/market-data.vue'),
      'utf8',
    )
    const scssSource = readFileSync(
      resolve(process.cwd(), 'src/views/converted.archive/styles/market-data.scss'),
      'utf8',
    )

    expect(vueSource).toContain("@use './styles/market-data.scss' as *;")
    expect(vueSource).not.toContain("@import './styles/market-data';")

    expect(scssSource).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(scssSource).toContain('var(--artdeco-gold-primary)')
    expect(scssSource).toContain('var(--artdeco-fg-primary)')
    expect(scssSource).toContain('var(--artdeco-fg-muted)')

    expect(scssSource).not.toContain("@import '@/styles/artdeco-tokens';")
    expect(scssSource).not.toContain('var(--artdeco-gold-hover)')
    expect(scssSource).not.toContain('var(--artdeco-up)')
    expect(scssSource).not.toContain('var(--artdeco-font-accent)')
    expect(scssSource).not.toContain('1200px')
    expect(scssSource).not.toContain('768px')
    expect(scssSource).not.toContain('rgb(212 175 55 / 5%)')
  })
})
