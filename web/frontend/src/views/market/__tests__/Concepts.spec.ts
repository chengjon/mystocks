import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/views/data/Concepts.vue', () => ({
  default: defineComponent({
    name: 'MockConceptsCanonicalPage',
    template: '<div class="canonical-concepts-page">概念板块工作台</div>',
  }),
}))

import Concepts from '../Concepts.vue'

describe('market/Concepts legacy wrapper truth', () => {
  it('delegates the legacy concepts page to the canonical /data/concept owner', () => {
    const wrapper = mount(Concepts as never)

    expect(wrapper.find('.canonical-concepts-page').exists()).toBe(true)
    expect(wrapper.text()).toContain('概念板块工作台')
    expect(wrapper.text()).not.toContain('CONCEPT MARKET DATA')
    expect(wrapper.text()).not.toContain('REFRESH ALL')
    expect(wrapper.text()).not.toContain('TOTAL CONCEPTS')
    expect(wrapper.text()).not.toContain('HOT CONCEPTS')
  })
})
