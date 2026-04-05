import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const riskWrapperFiles = [
  'src/views/risk/Alerts.vue',
  'src/views/risk/Overview.vue',
]

const riskPlaceholderFiles = [
  'src/views/risk/Portfolio.vue',
  'src/views/risk/Positions.vue',
]

describe('Risk style normalization', () => {
  it('keeps risk entry views off the legacy 20px spacing fallback', () => {
    const wrapperSources = riskWrapperFiles.map((file) => readFileSync(resolve(process.cwd(), file), 'utf8'))
    const placeholderSources = riskPlaceholderFiles.map((file) => readFileSync(resolve(process.cwd(), file), 'utf8'))

    for (const source of [...wrapperSources, ...placeholderSources]) {
      expect(source).not.toContain('padding: 20px')
    }

    for (const source of placeholderSources) {
      expect(source).toContain('var(--artdeco-spacing-5)')
    }
  })
})
