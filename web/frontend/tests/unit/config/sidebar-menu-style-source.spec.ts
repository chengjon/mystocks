import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('SidebarMenu style source', () => {
  it('keeps menu colors on ArtDeco token variables', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/layout/SidebarMenu.vue'), 'utf8')

    expect(source).toContain('text-color="var(--artdeco-fg-muted)"')
    expect(source).toContain('active-text-color="var(--artdeco-gold-primary)"')

    expect(source).not.toContain('text-color="#B8B8B8"')
    expect(source).not.toContain('active-text-color="#D4AF37"')
  })
})
