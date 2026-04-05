import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Demo styles mainline gate', () => {
  it('keeps demo styles covered by the demo directory gate', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/demo --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/demo/styles --changed-from-git')
  })
})
