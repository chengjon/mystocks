import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('TradeManagement style entrypoint', () => {
  it('keeps TradeManagement on @use and tokenized layout expressions', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/TradeManagement.vue'), 'utf8')

    expect(source).toContain("@use '@/styles/theme-tokens.scss' as *;")
    expect(source).not.toContain("@import '@/styles/theme-tokens';")
    expect(source).toContain('min-height: calc(var(--spacing-3xl) * 7 + var(--spacing-xl) + var(--spacing-md) + var(--spacing-xs));')
    expect(source).toContain('@media (width <= calc(var(--spacing-3xl) * 22 + var(--spacing-xl)))')
    expect(source).toContain('@media (width <= calc(var(--spacing-3xl) * 12))')
  })
})
