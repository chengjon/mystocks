import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('AnnouncementMonitor style source', () => {
  it('keeps AnnouncementMonitor styles on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/announcement/styles/AnnouncementMonitor.scss'),
      'utf8',
    )

    expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(source).toContain('background: var(--artdeco-bg-global);')
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('var(--bg-primary)')
    expect(source).not.toContain('var(--accent-gold)')
    expect(source).not.toContain('var(--spacing-')
    expect(source).not.toContain('#303133')
  })
})
