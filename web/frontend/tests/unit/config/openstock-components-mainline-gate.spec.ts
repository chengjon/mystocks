import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('OpenStock components mainline gate', () => {
  it('keeps openstock components covered by the demo directory gate without file-level fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/demo --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/demo/openstock/components --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/FeatureStatus.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/HeatmapChart.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/StockQuote.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/KlineChart.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/WatchlistManagement.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/StockSearch.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/openstock/components/StockNews.vue --changed-from-git')
  })
})
