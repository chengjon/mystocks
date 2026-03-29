import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling mainline gate', () => {
  it('keeps pyprofiling demo component files under changed-scope coverage', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-file src/views/demo/pyprofiling/components/Data.vue --changed-from-git')
    expect(pkg).toContain('--target-file src/views/demo/pyprofiling/components/Features.vue --changed-from-git')
    expect(pkg).toContain('--target-file src/views/demo/pyprofiling/components/API.vue --changed-from-git')
  })
})
