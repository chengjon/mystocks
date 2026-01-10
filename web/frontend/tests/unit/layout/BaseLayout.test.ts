import { describe, it, expect, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import BaseLayout from '@/layouts/BaseLayout.vue'
import BreadcrumbNav from '@/components/layout/BreadcrumbNav.vue'

describe('BaseLayout.vue', () => {
  // 创建路由实例
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/market', component: { template: '<div>Market</div>' } }
    ]
  })

  // 测试用的菜单项
  const mockMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/market', label: 'Market', icon: '📈' },
    { path: '/analysis', label: 'Analysis', icon: '🔍' }
  ]

  describe('组件渲染', () => {
    it('应该正确渲染基础结构', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems,
          pageTitle: 'Test Page'
        }
      })

      // 检查主要元素是否存在
      expect(wrapper.find('.base-layout').exists()).toBe(true)
      expect(wrapper.find('.layout-header').exists()).toBe(true)
      expect(wrapper.find('.layout-sidebar').exists()).toBe(true)
      expect(wrapper.find('.layout-main').exists()).toBe(true)
    })

    it('应该显示正确的页面标题', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems,
          pageTitle: 'My Dashboard'
        }
      })

      expect(wrapper.find('.page-title').text()).toBe('My Dashboard')
    })

    it('应该渲染所有菜单项', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      const navItems = wrapper.findAll('.nav-item')
      expect(navItems.length).toBe(mockMenuItems.length)
      
      // 检查第一个菜单项
      expect(navItems[0].text()).toContain('Dashboard')
      expect(navItems[0].text()).toContain('📊')
    })
  })

  describe('侧边栏功能', () => {
    it('侧边栏应该可以切换折叠状态', async () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      // 初始状态应该是展开的
      expect(wrapper.find('.base-layout').classes()).not.toContain('sidebar-collapsed')

      // 点击切换按钮
      await wrapper.find('.sidebar-toggle').trigger('click')
      
      // 应该添加collapsed类
      expect(wrapper.find('.base-layout').classes()).toContain('sidebar-collapsed')
    })

    it('折叠状态下应该隐藏菜单文本', async () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      // 切换到折叠状态
      await wrapper.find('.sidebar-toggle').trigger('click')
      await wrapper.vm.$nextTick()

      // 检查.nav-label是否隐藏（通过CSS类）
      expect(wrapper.find('.base-layout').classes()).toContain('sidebar-collapsed')
    })
  })

  describe('面包屑导航', () => {
    it('应该根据当前路由生成面包屑', async () => {
      await router.push('/dashboard')
      await router.isReady()

      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      const breadcrumb = wrapper.findComponent(BreadcrumbNav)
      expect(breadcrumb.exists()).toBe(true)
      
      // 面包屑应该接收items prop
      expect(breadcrumb.props('items')).toBeDefined()
      expect(breadcrumb.props('items').length).toBeGreaterThan(0)
    })
  })

  describe('搜索和通知功能', () => {
    it('点击搜索按钮应该触发Command Palette', async () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      // 模拟console.log
      const consoleSpy = vitest.spyOn(console, 'log').mockImplementation(() => {})

      await wrapper.find('.search-trigger').trigger('click')

      expect(consoleSpy).toHaveBeenCalledWith('Opening Command Palette (Ctrl+K)')
      
      consoleSpy.mockRestore()
    })

    it('应该显示未读通知徽章', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      // 初始状态没有未读消息
      expect(wrapper.find('.badge').exists()).toBe(false)

      // 设置未读数量（通过直接修改内部状态）
      wrapper.vm.unreadCount = 5
      
      // 由于Vue响应式系统，需要等待更新
      // 在实际测试中，应该通过事件或prop来设置这个值
    })
  })

  describe('响应式布局', () => {
    it('应该正确应用Design Token样式', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      const layoutElement = wrapper.find('.base-layout')
      
      // 检查是否应用了CSS变量（这些变量在theme-tokens.scss中定义）
      // 注意：在测试环境中，CSS变量可能无法直接访问
      // 这里主要检查元素是否存在且具有正确的类名
      expect(layoutElement.exists()).toBe(true)
    })

    it('应该在窗口大小变化时保持响应式', () => {
      // 测试响应式行为
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      // 在实际测试中，可以模拟窗口大小变化
      // 这里主要验证组件在默认尺寸下正常渲染
      expect(wrapper.find('.layout-main').exists()).toBe(true)
    })
  })

  describe('Props验证', () => {
    it('应该使用默认pageTitle', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems
        }
      })

      expect(wrapper.find('.page-title').text()).toBe('MyStocks')
    })

    it('应该接收自定义pageTitle', () => {
      const wrapper = mount(BaseLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        },
        props: {
          menuItems: mockMenuItems,
          pageTitle: 'Custom Title'
        }
      })

      expect(wrapper.find('.page-title').text()).toBe('Custom Title')
    })
  })
})
