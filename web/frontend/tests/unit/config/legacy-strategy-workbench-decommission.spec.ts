import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const retiredStyleFiles = [
  'src/views/strategy/styles/BatchScan.scss',
  'src/views/strategy/styles/ResultsQuery.scss',
  'src/views/strategy/styles/SingleRun.scss',
  'src/views/strategy/styles/StatsAnalysis.scss',
]

const legacyPages = [
  'src/views/strategy/BatchScan.vue',
  'src/views/strategy/ResultsQuery.vue',
  'src/views/strategy/SingleRun.vue',
  'src/views/strategy/StatsAnalysis.vue',
]

describe('legacy strategy workbench decommission guard', () => {
  it('keeps retired style files removed', () => {
    for (const file of retiredStyleFiles) {
      expect(existsSync(resolve(process.cwd(), file))).toBe(false)
    }
  })

  it('keeps legacy strategy workbench pages as static shells', () => {
    for (const file of legacyPages) {
      const source = readFileSync(resolve(process.cwd(), file), 'utf8')

      expect(source).toContain('legacy-static-shell')
      expect(source).toContain('canonical /strategy/* verified truth')
      expect(source).not.toContain('strategyApi.')
      expect(source).not.toContain('ElMessage')
      expect(source).not.toContain('@use "./styles/')
    }
  })
})
