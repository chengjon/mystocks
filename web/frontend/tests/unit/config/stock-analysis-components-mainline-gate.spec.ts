import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Stock analysis components mainline gate', () => {
  it('keeps stock-analysis demo components covered by the demo directory gate without file-level fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/demo --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/demo/stock-analysis/components --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/stock-analysis/components/Realtime.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/stock-analysis/components/Backtest.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/stock-analysis/components/Strategy.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/stock-analysis/components/DataParsing.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/stock-analysis/components/Status.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/stock-analysis/components/Overview.vue --changed-from-git')
  })
})
