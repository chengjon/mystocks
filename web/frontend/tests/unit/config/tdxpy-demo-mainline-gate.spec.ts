import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Tdxpy demo mainline gate', () => {
  it('keeps tdxpy-demo views under changed-scope directory coverage', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/tdxpy-demo --changed-from-git')
  })
})
