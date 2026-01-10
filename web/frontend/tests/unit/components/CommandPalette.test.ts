import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { nextTick } from 'vue'
import CommandPalette, { type CommandItem } from '@/components/shared/command-palette/CommandPalette.vue'

describe('CommandPalette.vue', () => {
  // 创建路由实例
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/market', component: { template: '<div>Market</div>' } },
      { path: '/analysis', component: { template: '<div>Analysis</div>' } }
    ]
  })

  // 测试用的命令项
  const mockCommandItems: CommandItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊', category: 'Main', keywords: ['dash', 'overview'] },
    { path: '/market', label: 'Market Data', icon: '📈', category: 'Data', keywords: ['market', 'stock'] },
    { path: '/analysis', label: 'Stock Analysis', icon: '🔍', category: 'Tools', keywords: ['analysis', 'screener'] }
  ]

  let wrapper: VueWrapper<InstanceType<typeof CommandPalette>>

  beforeEach(() => {
    wrapper = mount(CommandPalette, {
      global: {
        plugins: [router]
      },
      props: {
        items: mockCommandItems
      }
    })
  })

  describe('组件初始化', () => {
    it('应该正确渲染组件', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('初始状态应该是关闭的', () => {
      expect(wrapper.vm.isOpen).toBe(false)
    })

    it('应该接收命令项作为props', () => {
      expect(wrapper.props('items')).toEqual(mockCommandItems)
      expect(wrapper.props('items').length).toBe(3)
    })

    it('应该使用默认的maxRecent值', () => {
      expect(wrapper.props('maxRecent')).toBe(5)
    })

    it('应该接收自定义maxRecent值', () => {
      const customWrapper = mount(CommandPalette, {
        global: {
          plugins: [router]
        },
        props: {
          items: mockCommandItems,
          maxRecent: 10
        }
      })

      expect(customWrapper.props('maxRecent')).toBe(10)
    })
  })

  describe('打开和关闭功能', () => {
    it('应该能够打开Command Palette', async () => {
      wrapper.vm.open()
      await nextTick()

      expect(wrapper.vm.isOpen).toBe(true)
      expect(wrapper.find('.command-palette-overlay').exists()).toBe(true)
    })

    it('应该能够关闭Command Palette', async () => {
      wrapper.vm.open()
      await nextTick()

      wrapper.vm.close()
      await nextTick()

      expect(wrapper.vm.isOpen).toBe(false)
    })

    it('点击遮罩层应该关闭', async () => {
      wrapper.vm.open()
      await nextTick()

      const overlay = wrapper.find('.command-palette-overlay')
      await overlay.trigger('click')

      expect(wrapper.vm.isOpen).toBe(false)
    })

    it('打开时应该触发open事件', async () => {
      wrapper.vm.open()
      await nextTick()

      expect(wrapper.emitted('open')).toBeTruthy()
    })

    it('关闭时应该触发close事件', async () => {
      wrapper.vm.open()
      await nextTick()

      wrapper.vm.close()
      await nextTick()

      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('搜索功能', () => {
    beforeEach(async () => {
      wrapper.vm.open()
      await nextTick()
    })

    it('应该能够输入搜索查询', async () => {
      const input = wrapper.find('.search-input')
      await input.setValue('dash')

      expect(wrapper.vm.searchQuery).toBe('dash')
    })

    it('应该显示搜索结果', async () => {
      const input = wrapper.find('.search-input')
      await input.setValue('market')
      await nextTick()

      const results = wrapper.vm.searchResults
      expect(results.length).toBeGreaterThan(0)
      expect(results[0].item.label).toBe('Market Data')
    })

    it('模糊搜索应该工作正常', async () => {
      const input = wrapper.find('.search-input')
      
      // 搜索关键词
      await input.setValue('dash')
      await nextTick()
      expect(wrapper.vm.searchResults.length).toBeGreaterThan(0)

      await input.setValue('stock')
      await nextTick()
      expect(wrapper.vm.searchResults.length).toBeGreaterThan(0)
    })

    it('无搜索结果时应该显示提示', async () => {
      const input = wrapper.find('.search-input')
      await input.setValue('nonexistent')
      await nextTick()

      expect(wrapper.vm.searchResults.length).toBe(0)
      expect(wrapper.find('.no-results').exists()).toBe(true)
    })
  })

  describe('键盘导航', () => {
    beforeEach(async () => {
      wrapper.vm.open()
      await nextTick()

      // 输入搜索查询以生成结果
      const input = wrapper.find('.search-input')
      await input.setValue('data')
      await nextTick()
    })

    it('应该能够使用上下箭头键导航', async () => {
      const input = wrapper.find('.search-input') as any

      // 按下箭头
      await input.trigger('keydown', { key: 'ArrowDown' })
      expect(wrapper.vm.selectedIndex).toBe(1)

      // 按上箭头
      await input.trigger('keydown', { key: 'ArrowUp' })
      expect(wrapper.vm.selectedIndex).toBe(0)
    })

    it('应该能够使用Enter键选择结果', async () => {
      const navigateSpy = vi.spyOn(wrapper.vm, 'navigateTo')
      const input = wrapper.find('.search-input') as any

      await input.trigger('keydown', { key: 'Enter' })

      expect(navigateSpy).toHaveBeenCalled()
    })

    it('应该能够使用Esc键关闭', async () => {
      const input = wrapper.find('.search-input') as any

      await input.trigger('keydown', { key: 'Escape' })
      await nextTick()

      expect(wrapper.vm.isOpen).toBe(false)
    })
  })

  describe('鼠标交互', () => {
    beforeEach(async () => {
      wrapper.vm.open()
      await nextTick()

      const input = wrapper.find('.search-input')
      await input.setValue('market')
      await nextTick()
    })

    it('点击结果项应该导航', async () => {
      const pushSpy = vi.spyOn(router, 'push')
      const resultItems = wrapper.findAll('.result-item')
      
      if (resultItems.length > 0) {
        await resultItems[0].trigger('click')
        await nextTick()

        expect(pushSpy).toHaveBeenCalled()
      }
    })

    it('鼠标悬停应该更新selectedIndex', async () => {
      const resultItems = wrapper.findAll('.result-item')
      
      if (resultItems.length > 1) {
        await resultItems[1].trigger('mouseenter')
        expect(wrapper.vm.selectedIndex).toBe(1)
      }
    })
  })

  describe('最近访问历史', () => {
    beforeEach(async () => {
      wrapper.vm.open()
      await nextTick()
    })

    it('空搜索时应该显示最近访问', async () => {
      // 手动设置最近访问
      wrapper.vm.recentItems = [mockCommandItems[0]]
      await nextTick()

      const recentSection = wrapper.find('.result-section')
      expect(recentSection.exists()).toBe(true)
      expect(wrapper.find('.section-title').text()).toBe('Recent')
    })

    it('应该能够添加到最近访问', () => {
      wrapper.vm.addToRecent('/market')

      expect(wrapper.vm.recentItems.length).toBe(1)
      expect(wrapper.vm.recentItems[0].path).toBe('/market')
    })

    it('应该限制最近访问数量', () => {
      // 添加超过maxRecent数量的项
      for (let i = 0; i < 10; i++) {
        wrapper.vm.addToRecent(`/path${i}`)
      }

      expect(wrapper.vm.recentItems.length).toBeLessThanOrEqual(wrapper.props('maxRecent'))
    })

    it('重复路径应该移到开头', () => {
      wrapper.vm.addToRecent('/path1')
      wrapper.vm.addToRecent('/path2')
      wrapper.vm.addToRecent('/path1') // 重复添加

      expect(wrapper.vm.recentItems[0].path).toBe('/path1')
    })
  })

  describe('文本高亮', () => {
    it('应该高亮匹配的文本', () => {
      wrapper.vm.searchQuery = 'dash'

      const highlighted = wrapper.vm.highlightMatch('Dashboard')
      expect(highlighted).toContain('<mark>dash</mark>')
    })

    it('无匹配时不应该高亮', () => {
      wrapper.vm.searchQuery = 'xyz'

      const highlighted = wrapper.vm.highlightMatch('Dashboard')
      expect(highlighted).toBe('Dashboard')
    })

    it('空搜索时不应该高亮', () => {
      wrapper.vm.searchQuery = ''

      const highlighted = wrapper.vm.highlightMatch('Dashboard')
      expect(highlighted).toBe('Dashboard')
    })
  })

  describe('暴露的方法', () => {
    it('应该暴露open方法', () => {
      expect(typeof wrapper.vm.open).toBe('function')
    })

    it('应该暴露close方法', () => {
      expect(typeof wrapper.vm.close).toBe('function')
    })

    it('父组件应该能够调用open方法', async () => {
      wrapper.vm.open()
      await nextTick()

      expect(wrapper.vm.isOpen).toBe(true)
    })

    it('父组件应该能够调用close方法', async () => {
      wrapper.vm.open()
      await nextTick()

      wrapper.vm.close()
      await nextTick()

      expect(wrapper.vm.isOpen).toBe(false)
    })
  })
})
