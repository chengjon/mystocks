import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('market realtime accessibility guards', () => {
  it('keeps the market realtime content title at h2 level', () => {
    const source = readSource('src/views/market/Realtime.vue')

    expect(source).toContain('<h2 class="content-shell-title">样本快照与分布面板</h2>')
  })

  it('gives the market realtime sample selector an explicit accessible label', () => {
    const source = readSource('src/views/market/Realtime.vue')

    expect(source).toMatch(/<ArtDecoSelect\s+v-model="activePreset"[\s\S]*label="观察样本"/)
  })

  it('forwards an explicit label prop to the native select accessible name', () => {
    const wrapper = mount(ArtDecoSelect, {
      props: {
        modelValue: 'today',
        label: '统计窗口',
        options: [
          { label: '今日', value: 'today' },
          { label: '3日', value: '3d' }
        ]
      }
    })

    expect(wrapper.get('select').attributes('aria-label')).toBe('统计窗口')
  })
})
