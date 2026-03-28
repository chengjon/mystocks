import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('monitoring style sources', () => {
  it('keeps monitoring styles on ArtDeco token imports and variables', () => {
    const files = [
      'src/views/monitoring/styles/AlertRulesManagement.scss',
      'src/views/monitoring/styles/MonitoringDashboard.scss',
    ]

    for (const file of files) {
      const source = readSource(file)

      expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
      expect(source).toContain('var(--artdeco-')
      expect(source).not.toContain('var(--bg-primary)')
      expect(source).not.toContain('var(--gold-primary)')
      expect(source).not.toContain('var(--text-primary)')
      expect(source).not.toContain('var(--text-muted)')
    }
  })
})
