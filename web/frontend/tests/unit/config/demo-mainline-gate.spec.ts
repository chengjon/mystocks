import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Demo mainline gate', () => {
  it('keeps demo views under changed-scope directory coverage without child fallback entries', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/demo --changed-from-git')

    expect(pkg).not.toContain('--target-dir src/views/demo/styles --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/demo/pyprofiling/components --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/demo/openstock/components --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/demo/stock-analysis/components --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/Phase4Dashboard.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/Wencai.vue --changed-from-git')
  })
})
