import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Strategy styles mainline gate', () => {
  it('keeps strategy views under changed-scope directory coverage without redundant strategy file entries', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/strategy --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/strategy/styles --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/BatchScan.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/SingleRun.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/StatsAnalysis.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/ResultsQuery.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/StrategyList.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/BacktestGPU.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/strategy/styles/ResultsQuery.scss --changed-from-git')
  })
})
