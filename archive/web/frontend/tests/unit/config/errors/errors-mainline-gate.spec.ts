import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Errors mainline gate', () => {
  it('keeps error views under changed-scope directory coverage without file-level fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/errors --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/errors/ServiceUnavailable.vue --changed-from-git')
  })
})
