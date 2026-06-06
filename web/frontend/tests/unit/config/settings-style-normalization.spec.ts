import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const settingsFiles = [
  'src/views/settings/General.vue',
  'src/views/settings/Notifications.vue',
  'src/views/settings/Security.vue',
  'src/views/settings/Theme.vue',
]

describe('Settings style normalization', () => {
  it('keeps retired placeholder settings views as honest static shells', () => {
    const sources = settingsFiles.map((file) => readFileSync(resolve(process.cwd(), file), 'utf8'))

    for (const source of sources) {
      expect(source).toContain('legacy-static-shell')
      expect(source).toContain('canonical /system/config')
      expect(source).toContain('var(--artdeco-spacing-5)')
      expect(source).not.toContain('placeholder-content')
      expect(source).not.toContain('<el-alert')
      expect(source).not.toContain('Coming Soon')
      expect(source).not.toContain('padding: 20px')
    }
  })
})
