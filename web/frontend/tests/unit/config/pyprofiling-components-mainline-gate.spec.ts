import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling components mainline gate', () => {
  it('keeps pyprofiling components under changed-scope directory coverage without file-level fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/demo/pyprofiling/components --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/pyprofiling/components/Prediction.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/pyprofiling/components/Data.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/pyprofiling/components/Features.vue --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/demo/pyprofiling/components/API.vue --changed-from-git')
  })
})
