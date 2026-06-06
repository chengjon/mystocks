import { mount } from '@vue/test-utils'
import { computed, ref } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import ArtDecoLanguageSwitcher from '@/components/artdeco/base/ArtDecoLanguageSwitcher.vue'

const setLocale = vi.fn()
const locale = ref('zh-CN')
const supportedLocales = [
  { code: 'zh-CN', name: 'Simplified Chinese', flag: 'CN' },
  { code: 'en-US', name: 'English', flag: 'US' }
] as const

vi.mock('@/composables/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) =>
      ({
        'accessibility.changeLanguage': 'Change language',
        'settings.language': 'Language'
      })[key] ?? key,
    locale: computed(() => locale.value),
    localeInfo: computed(() => supportedLocales.find(item => item.code === locale.value)),
    supportedLocales: computed(() => supportedLocales),
    setLocale
  })
}))

const global = {
  mocks: {
    $t: (key: string) =>
      ({
        'accessibility.changeLanguage': 'Change language',
        'settings.language': 'Language'
      })[key] ?? key
  },
  stubs: {
    ElDropdown: {
      template: '<div class="el-dropdown-stub"><slot /><slot name="dropdown" /></div>'
    },
    ElDropdownMenu: {
      template: '<div class="el-dropdown-menu-stub"><slot /></div>'
    },
    ElDropdownItem: {
      template: '<div class="el-dropdown-menu__item"><slot /></div>'
    }
  }
}

describe('ArtDecoLanguageSwitcher accessibility contract', () => {
  it('exposes menu button and listbox semantics without reading decorative flags', () => {
    const wrapper = mount(ArtDecoLanguageSwitcher, { global })

    const button = wrapper.get('button.language-button')
    const listbox = wrapper.get('[role="listbox"]')
    const options = wrapper.findAll('[role="option"]')

    expect(button.attributes('aria-label')).toBe('Change language')
    expect(button.attributes('aria-expanded')).toBe('false')
    expect(button.attributes('aria-haspopup')).toBe('listbox')
    expect(button.get('.language-flag').attributes('aria-hidden')).toBe('true')

    expect(listbox.attributes('aria-label')).toBe('Language')
    expect(options).toHaveLength(2)
    expect(options[0].attributes('aria-selected')).toBe('true')
    expect(options[1].attributes('aria-selected')).toBe('false')
    expect(wrapper.findAll('.locale-flag').every(flag => flag.attributes('aria-hidden') === 'true')).toBe(true)
  })
})
