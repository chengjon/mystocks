import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Pyprofiling mainline gate', () => {
  it('keeps Data.vue under changed-scope coverage for pyprofiling demo components', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-file src/views/demo/pyprofiling/components/Data.vue --changed-from-git')
  })
})
