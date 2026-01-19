/**
 * BaseLayout Integration Tests
 *
 * 验证BaseLayout.vue中错误处理和数据获取的集成
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import BaseLayout from '@/layouts/BaseLayout.vue'
import { ARTDECO_MENU_ITEMS } from '@/layouts/MenuConfig'
import { useToastManager } from '@/composables/useToastManager'

// Mock useStorage
vi.mock('@/composables/useStorage', () => ({
  useStorage: (key: string, defaultValue: any) => {
    return vi.fn(() => defaultValue)()
  }
}))

// Mock useWebSocket
vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: () => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
    subscribe: vi.fn(() => vi.fn()),
    message: { value: null }
  })
}))

// Mock fetchMenuItemData
vi.mock('@/services/menuDataFetcher', () => ({
  fetchMenuItemData: vi.fn(),
  clearMenuDataCache: vi.fn()
}))

// Mock apiClient
vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

import { fetchMenuItemData, clearMenuDataCache } from '@/services/menuDataFetcher'

describe('BaseLayout集成测试', () => {
  let wrapper: VueWrapper<any>
  let toast: ReturnType<typeof useToastManager>

  beforeEach(() => {
    // 创建Pinia实例
    setActivePinia(createPinia())

    // 初始化Toast管理器
    toast = useToastManager()
    toast.clearAll()

    // 挂载组件
    wrapper = mount(BaseLayout, {
      props: {
        pageTitle: 'MyStocks',
        menuItems: ARTDECO_MENU_ITEMS
      },
      global: {
        stubs: {
          BreadcrumbNav: true,
          CommandPalette: true,
          ArtDecoToast: true,
          ArtDecoIcon: true,
          ArtDecoBadge: true,
          'router-link': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
    toast.clearAll()
  })

  describe('组件初始化', () => {
    it('应该正确渲染', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.base-layout').exists()).toBe(true)
    })

    it('应该显示页面标题', () => {
      expect(wrapper.find('.page-title').text()).toBe('MyStocks')
    })

    it('应该渲染所有菜单项', () => {
      const navItems = wrapper.findAll('.nav-item')
      expect(navItems).toHaveLength(ARTDECO_MENU_ITEMS.length)
    })

    it('应该有Toast组件', () => {
      expect(wrapper.findComponent({ name: 'ArtDecoToast' }).exists()).toBe(true)
    })
  })

  describe('错误处理功能', () => {
    it('handleNavigationError应该标记菜单项为错误状态', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      const mockEvent = new Error('Navigation failed')

      await wrapper.vm.handleNavigationError(mockEvent, menuItem)

      expect(menuItem.error).toBe(true)
    })

    it('handleNavigationError应该显示错误Toast', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      const mockEvent = new Error('Navigation failed')

      await wrapper.vm.handleNavigationError(mockEvent, menuItem)

      // 验证Toast显示
      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('error')
      expect(toast.toasts[0].message).toContain('无法加载')
      expect(toast.toasts[0].message).toContain(menuItem.label)
    })

    it('showErrorToast应该正确显示错误通知', () => {
      wrapper.vm.showErrorToast('测试错误消息', '错误标题')

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('error')
      expect(toast.toasts[0].message).toBe('测试错误消息')
      expect(toast.toasts[0].title).toBe('错误标题')
    })

    it('showSuccessToast应该正确显示成功通知', () => {
      wrapper.vm.showSuccessToast('操作成功', '成功')

      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('success')
      expect(toast.toasts[0].message).toBe('操作成功')
      expect(toast.toasts[0].title).toBe('成功')
    })
  })

  describe('数据获取功能', () => {
    it('fetchItemData应该成功获取菜单数据', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      const mockData = { summary: 'test data' }

      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: true,
        data: mockData,
        cached: false
      })

      const result = await wrapper.vm.fetchItemData(menuItem)

      expect(result).toEqual(mockData)
      expect(fetchMenuItemData).toHaveBeenCalledWith(
        menuItem,
        expect.objectContaining({
          timeout: 10000,
          retries: 2,
          cache: true
        })
      )
    })

    it('fetchItemData应该更新lastUpdate时间戳（非缓存数据）', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      const beforeTimestamp = menuItem.lastUpdate

      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: true,
        data: { test: true },
        cached: false
      })

      await wrapper.vm.fetchItemData(menuItem)

      expect(menuItem.lastUpdate).toBeGreaterThanOrEqual(beforeTimestamp || 0)
    })

    it('fetchItemData不应该更新lastUpdate时间戳（缓存数据）', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      const originalTimestamp = menuItem.lastUpdate

      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: true,
        data: { test: true },
        cached: true
      })

      await wrapper.vm.fetchItemData(menuItem)

      expect(menuItem.lastUpdate).toBe(originalTimestamp)
    })

    it('fetchItemData应该处理缺失apiEndpoint的菜单项', async () => {
      const menuItem: any = {
        path: '/test',
        label: '测试',
        icon: 'test'
        // 缺少apiEndpoint
      }

      const result = await wrapper.vm.fetchItemData(menuItem)

      expect(result).toBeNull()
    })

    it('fetchItemData应该处理API错误', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      const mockError = new Error('API Error')

      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: false,
        error: mockError.message
      })

      await expect(wrapper.vm.fetchItemData(menuItem)).rejects.toThrow('API Error')
    })
  })

  describe('重试机制', () => {
    it('retryApiCall应该成功重试并清除错误状态', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      menuItem.error = true

      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: true,
        data: { test: true },
        cached: false
      })

      await wrapper.vm.retryApiCall(menuItem)

      expect(clearMenuDataCache).toHaveBeenCalledWith(menuItem.apiEndpoint)
      expect(menuItem.error).toBe(false)
      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('success')
      expect(toast.toasts[0].message).toContain('数据已成功重新加载')
    })

    it('retryApiCall应该保持错误状态（重试失败）', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      menuItem.error = true

      const mockError = new Error('Retry failed')
      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: false,
        error: mockError.message
      })

      await wrapper.vm.retryApiCall(menuItem)

      expect(clearMenuDataCache).toHaveBeenCalledWith(menuItem.apiEndpoint)
      expect(menuItem.error).toBe(true)
      expect(toast.toasts).toHaveLength(1)
      expect(toast.toasts[0].type).toBe('error')
      expect(toast.toasts[0].message).toContain('重新加载')
      expect(toast.toasts[0].message).toContain('失败')
    })

    it('retryApiCall应该清除缓存', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]
      menuItem.error = true

      vi.mocked(fetchMenuItemData).mockResolvedValue({
        success: true,
        data: { test: true },
        cached: false
      })

      await wrapper.vm.retryApiCall(menuItem)

      expect(clearMenuDataCache).toHaveBeenCalledWith(menuItem.apiEndpoint)
    })
  })

  describe('Toast集成', () => {
    it('应该传递toasts到ArtDecoToast组件', () => {
      const toastComponent = wrapper.findComponent({ name: 'ArtDecoToast' })

      expect(toastComponent.props('toasts')).toEqual(toast.toasts)
      expect(toastComponent.props('position')).toBe('top-right')
    })

    it('应该处理Toast关闭事件', async () => {
      const toastId = toast.showError('测试错误')
      expect(toast.toasts).toHaveLength(1)

      const toastComponent = wrapper.findComponent({ name: 'ArtDecoToast' })
      await toastComponent.vm.$emit('close', toastId)

      expect(toast.toasts).toHaveLength(0)
    })
  })

  describe('响应式状态', () => {
    it('侧边栏折叠状态应该可切换', async () => {
      expect(wrapper.vm.sidebarCollapsed).toBe(false)

      await wrapper.vm.toggleSidebar()

      expect(wrapper.vm.sidebarCollapsed).toBe(true)

      await wrapper.vm.toggleSidebar()

      expect(wrapper.vm.sidebarCollapsed).toBe(false)
    })

    it('菜单项应该响应式更新', async () => {
      const menuItem = ARTDECO_MENU_ITEMS[0]

      expect(wrapper.vm.menuItemsRef).toContain(menuItem)

      // 模拟状态更新
      menuItem.status = 'loading'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.menuItemsRef[0].status).toBe('loading')
    })
  })

  describe('时间格式化', () => {
    it('formatTime应该正确格式化Unix时间戳', () => {
      const timestamp = 1642694400 // 2022-01-20 12:00:00
      const formatted = wrapper.vm.formatTime(timestamp)

      expect(formatted).toMatch(/^\d{2}:\d{2}:\d{2}$/)
    })

    it('formatTime应该使用中文格式', () => {
      const timestamp = 1642694400
      const formatted = wrapper.vm.formatTime(timestamp)

      expect(formatted).toContain(':')
      expect(formatted).toMatch(/\d{2}:\d{2}:\d{2}/)
    })
  })

  describe('路由集成', () => {
    it('isActive应该正确识别活动路由', () => {
      // Mock route
      wrapper.vm.route = { path: '/dashboard' }

      expect(wrapper.vm.isActive('/dashboard')).toBe(true)
      expect(wrapper.vm.isActive('/market/data')).toBe(false)
    })

    it('应该生成正确的面包屑', () => {
      // Mock route
      wrapper.vm.route = { path: '/dashboard/overview' }

      const breadcrumbs = wrapper.vm.breadcrumbItems

      expect(breadcrumbs).toHaveLength(2)
      expect(breadcrumbs[0].label).toBe('Home')
      expect(breadcrumbs[1].label).toBe('Dashboard')
    })
  })

  describe('Command Palette集成', () => {
    it('应该打开Command Palette', () => {
      const openSpy = vi.spyOn(wrapper.vm.commandPaletteRef, 'open')

      wrapper.vm.openCommandPalette()

      expect(openSpy).toHaveBeenCalled()
    })

    it('应该生成正确的命令项', () => {
      const commandItems = wrapper.vm.commandItems

      expect(commandItems).toHaveLength(ARTDECO_MENU_ITEMS.length)

      commandItems.forEach((item: any, index: number) => {
        expect(item.path).toBe(ARTDECO_MENU_ITEMS[index].path)
        expect(item.label).toBe(ARTDECO_MENU_ITEMS[index].label)
        expect(item.category).toBe('MyStocks')
      })
    })
  })
})
