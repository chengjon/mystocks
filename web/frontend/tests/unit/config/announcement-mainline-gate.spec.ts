import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Announcement mainline gate', () => {
  it('keeps announcement views under changed-scope directory coverage without file-level fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/announcement --changed-from-git')
    expect(pkg).not.toContain('--target-file src/views/announcement/AnnouncementMonitor.vue --changed-from-git')
  })
})
