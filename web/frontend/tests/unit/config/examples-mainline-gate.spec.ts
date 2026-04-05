import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Examples mainline gate', () => {
  it('keeps examples views under changed-scope directory coverage', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/examples --changed-from-git')
  })
})
