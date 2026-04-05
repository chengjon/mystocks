import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
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
  setup(props, { expose }) {
    const openCalled = ref(false)

    const open = () => {
      openCalled.value = true
    }

    expose({
      open
    })

    return () =>
      h('div', {
        class: 'command-palette-stub',
        'data-item-count': String(props.items.length),
        'data-open-called': String(openCalled.value)
      })
  }
})

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: 'Home' },
  { path: '/market', label: 'Market', icon: 'Trend' },
  { path: '/analysis', label: 'Analysis', icon: 'Search' }
]

const mountNavigationShell = async (routePath = '/dashboard') => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/market', component: { template: '<div>Market</div>' } },
      { path: '/analysis', component: { template: '<div>Analysis</div>' } }
    ]
  })

  await router.push(routePath)
  await router.isReady()

  const wrapper = mount(BaseLayout, {
    props: {
      pageTitle: 'Navigation Test',
      menuItems
    },
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
    }
  })

  await nextTick()

  return { wrapper, router }
}

describe('BaseLayout navigation shell', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
  })

  it('renders the breadcrumb shell for the current route', async () => {
    ;({ wrapper } = await mountNavigationShell('/dashboard'))

    const breadcrumb = wrapper.findComponent(ArtDecoBreadcrumbStub)
    expect(breadcrumb.exists()).toBe(true)
    expect(breadcrumb.props('homeTitle')).toBe('交易室')
    expect(breadcrumb.props('homePath')).toBe('/dashboard')
  })

  it('maps layout menu items into command palette items', async () => {
    ;({ wrapper } = await mountNavigationShell('/dashboard'))

    const palette = wrapper.findComponent(CommandPaletteStub)
    const commandItems = (wrapper.vm as unknown as { commandItems: Array<Record<string, unknown>> }).commandItems

    expect(palette.attributes('data-item-count')).toBe(String(menuItems.length))
    expect(commandItems[0]).toMatchObject({
      path: '/dashboard',
      label: 'Dashboard',
      category: 'Navigation Test'
    })
  })

  it('opens the command palette from the search trigger', async () => {
    ;({ wrapper } = await mountNavigationShell('/dashboard'))

    const palette = wrapper.findComponent(CommandPaletteStub)
    expect(palette.attributes('data-open-called')).toBe('false')

    await wrapper.find('.search-trigger').trigger('click')
    await nextTick()

    expect(palette.attributes('data-open-called')).toBe('true')
  })

  it('marks the active navigation item based on the current route', async () => {
    const mounted = await mountNavigationShell('/market')
    wrapper = mounted.wrapper

    const navItems = wrapper.findAll('.nav-item')
    expect(navItems).toHaveLength(menuItems.length)
    expect(navItems[1].classes()).toContain('active')
    expect(navItems[0].classes()).not.toContain('active')
  })

  it('updates the document title using the current page title', async () => {
    ;({ wrapper } = await mountNavigationShell('/analysis'))

    expect(document.title).toBe('Navigation Test - MyStocks')
  })
})
