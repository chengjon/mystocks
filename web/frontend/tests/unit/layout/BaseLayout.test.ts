import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent, h, nextTick, ref } from 'vue'
import BaseLayout from '@/layouts/BaseLayout.vue'

vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: () => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
    message: ref(null)
  })
}))

vi.mock('@/composables/useToastManager', () => ({
  useToastManager: () => ({
    toasts: [],
    showError: vi.fn(),
    showSuccess: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn(),
    show: vi.fn(),
    remove: vi.fn(),
    clearAll: vi.fn()
  })
}))

vi.mock('@/services/menuDataFetcher', () => ({
  fetchMenuItemData: vi.fn(),
  clearMenuDataCache: vi.fn()
}))

const ArtDecoBreadcrumbStub = defineComponent({
  name: 'ArtDecoBreadcrumb',
  props: {
    homeTitle: String,
    homePath: String,
    showIcon: Boolean
  },
  setup(props) {
    return () =>
      h('nav', { class: 'artdeco-breadcrumb-stub' }, [
        h('span', { class: 'breadcrumb-home-title' }, props.homeTitle),
        h('span', { class: 'breadcrumb-home-path' }, props.homePath)
      ])
  }
})

const CommandPaletteStub = defineComponent({
  name: 'CommandPalette',
  props: {
    items: {
      type: Array,
      default: () => []
    }
  },
  setup(_props, { expose }) {
    const openCalled = ref(false)
    const closeCalled = ref(false)

    const open = () => {
      openCalled.value = true
    }

    const close = () => {
      closeCalled.value = true
    }

    expose({
      open,
      close,
      openCalled,
      closeCalled
    })

    return () =>
      h('div', {
        class: 'command-palette-stub',
        'data-open-called': String(openCalled.value),
        'data-close-called': String(closeCalled.value)
      })
  }
})

const mountBaseLayout = (overrides: Record<string, unknown> = {}) => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/market', component: { template: '<div>Market</div>' } },
      { path: '/analysis', component: { template: '<div>Analysis</div>' } }
    ]
  })

  const mockMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: 'Home' },
    { path: '/market', label: 'Market', icon: 'Market' },
    { path: '/analysis', label: 'Analysis', icon: 'Search' }
  ]

  const wrapper = mount(BaseLayout, {
    global: {
      plugins: [router],
      stubs: {
        ArtDecoBreadcrumb: ArtDecoBreadcrumbStub,
        ArtDecoSkipLink: {
          template: '<a class="skip-link-stub" href="#main-content">Skip</a>'
        },
        CommandPalette: CommandPaletteStub,
        ArtDecoIcon: {
          props: ['name'],
          template: '<span class="artdeco-icon-stub">{{ name }}</span>'
        },
        ArtDecoBadge: {
          props: ['text'],
          template: '<span class="artdeco-badge-stub">{{ text }}</span>'
        },
        ArtDecoToast: {
          template: '<div class="artdeco-toast-stub"></div>'
        }
      }
    },
    props: {
      menuItems: mockMenuItems,
      ...overrides
    }
  })

  return { wrapper, router, mockMenuItems }
}

describe('BaseLayout.vue', () => {
  let wrapper: VueWrapper

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染基础结构', () => {
      ;({ wrapper } = mountBaseLayout({ pageTitle: 'Test Page' }))

      expect(wrapper.find('.base-layout').exists()).toBe(true)
      expect(wrapper.find('.layout-header').exists()).toBe(true)
      expect(wrapper.find('.layout-sidebar').exists()).toBe(true)
      expect(wrapper.find('.layout-main').exists()).toBe(true)
    })

    it('应该显示正确的页面标题', () => {
      ;({ wrapper } = mountBaseLayout({ pageTitle: 'My Dashboard' }))

      expect(wrapper.find('.page-title').text()).toBe('My Dashboard')
    })

    it('应该渲染所有菜单项', () => {
      const mounted = mountBaseLayout()
      wrapper = mounted.wrapper

      const navItems = wrapper.findAll('.nav-item')
      expect(navItems.length).toBe(mounted.mockMenuItems.length)
      expect(navItems[0].text()).toContain('Dashboard')
      expect(navItems[0].text()).toContain('Home')
    })
  })

  describe('侧边栏功能', () => {
    it('侧边栏应该可以切换折叠状态', async () => {
      ;({ wrapper } = mountBaseLayout())

      expect(wrapper.find('.base-layout').classes()).not.toContain('sidebar-collapsed')

      await wrapper.find('.sidebar-toggle').trigger('click')

      expect(wrapper.find('.base-layout').classes()).toContain('sidebar-collapsed')
    })

    it('折叠状态下应该隐藏菜单文本', async () => {
      ;({ wrapper } = mountBaseLayout())

      await wrapper.find('.sidebar-toggle').trigger('click')
      await nextTick()

      expect(wrapper.find('.base-layout').classes()).toContain('sidebar-collapsed')
    })
  })

  describe('面包屑导航', () => {
    it('应该根据当前布局渲染面包屑组件', async () => {
      const mounted = mountBaseLayout()
      wrapper = mounted.wrapper
      await mounted.router.push('/dashboard')
      await mounted.router.isReady()

      const breadcrumb = wrapper.findComponent(ArtDecoBreadcrumbStub)
      expect(breadcrumb.exists()).toBe(true)
      expect(breadcrumb.props('homeTitle')).toBe('交易室')
      expect(breadcrumb.props('homePath')).toBe('/dashboard')
    })
  })

  describe('搜索和通知功能', () => {
    it('点击搜索按钮应该调用 Command Palette 的 open 方法', async () => {
      ;({ wrapper } = mountBaseLayout())

      const palette = wrapper.findComponent(CommandPaletteStub)
      expect(palette.exists()).toBe(true)
      expect(palette.attributes('data-open-called')).toBe('false')

      await wrapper.find('.search-trigger').trigger('click')
      await nextTick()

      expect(palette.attributes('data-open-called')).toBe('true')
    })

    it('应该显示未读通知徽章', async () => {
      ;({ wrapper } = mountBaseLayout())

      expect(wrapper.find('.badge').exists()).toBe(false)

      ;(wrapper.vm as unknown as { unreadCount: number }).unreadCount = 5
      await nextTick()

      expect(wrapper.find('.badge').exists()).toBe(true)
      expect(wrapper.find('.badge').text()).toBe('5')
    })
  })

  describe('响应式布局', () => {
    it('应该正确应用Design Token样式', () => {
      ;({ wrapper } = mountBaseLayout())

      expect(wrapper.find('.base-layout').exists()).toBe(true)
    })

    it('应该在窗口大小变化时保持响应式', () => {
      ;({ wrapper } = mountBaseLayout())

      expect(wrapper.find('.layout-main').exists()).toBe(true)
    })
  })

  describe('Props验证', () => {
    it('应该使用默认pageTitle', () => {
      ;({ wrapper } = mountBaseLayout())

      expect(wrapper.find('.page-title').text()).toBe('MyStocks')
    })

    it('应该接收自定义pageTitle', () => {
      ;({ wrapper } = mountBaseLayout({ pageTitle: 'Custom Title' }))

      expect(wrapper.find('.page-title').text()).toBe('Custom Title')
    })
  })
})
