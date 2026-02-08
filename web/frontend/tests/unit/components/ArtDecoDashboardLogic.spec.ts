import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ArtDecoDashboard from '@/views/artdeco-pages/ArtDecoDashboard.vue'
import { createPinia, setActivePinia } from 'pinia'
import { usePreferenceStore } from '@/stores/preferenceStore'
import dashboardService from '@/api/services/dashboardService'
import { mockWebSocket } from '@/api/mockWebSocket'

// Mock dependencies
vi.mock('@/api/services/dashboardService', () => ({
  default: {
    getMarketOverview: vi.fn().mockResolvedValue({ data: [] }),
    getFundFlow: vi.fn().mockResolvedValue({ data: {} }),
    getIndustryFlow: vi.fn().mockResolvedValue({ data: [] }),
    getStockFlowRanking: vi.fn().mockResolvedValue({ data: [] })
  }
}))

vi.mock('@/api/mockWebSocket', () => ({
  mockWebSocket: {
    subscribe: vi.fn(),
    unsubscribe: vi.fn()
  }
}))

// Mock router-link
const RouterLinkStub = {
  template: '<a><slot /></a>',
  props: ['to']
}

describe('ArtDecoDashboard Logic Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    
    // Mock localStorage
    const localStorageMock = (() => {
      let store: Record<string, string> = {}
      return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => { store[key] = value },
        clear: () => { store = {} }
      }
    })()
    Object.defineProperty(window, 'localStorage', { value: localStorageMock })
  })

  it('should initialize with correct default loading states', async () => {
    const wrapper = mount(ArtDecoDashboard, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
          'ArtDecoChart': true // Stub complex chart
        }
      }
    })

    // Access internal state via vm if needed or check rendered skeletons
    expect(wrapper.findComponent({ name: 'ArtDecoHeader' }).exists()).toBe(true)
  })

  it('should call dashboard services on mount', async () => {
    mount(ArtDecoDashboard, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
          'ArtDecoChart': true
        }
      }
    })

    expect(dashboardService.getMarketOverview).toHaveBeenCalled()
    expect(dashboardService.getFundFlow).toHaveBeenCalled()
    expect(dashboardService.getIndustryFlow).toHaveBeenCalled()
  })

  it('should subscribe to WebSocket on mount', async () => {
    mount(ArtDecoDashboard, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
          'ArtDecoChart': true
        }
      }
    })

    expect(mockWebSocket.subscribe).toHaveBeenCalledWith(
      expect.stringContaining('market.trend'),
      expect.any(Function)
    )
  })

  it('should integrate with preferenceStore for collapse states', async () => {
    // Setup localStorage with saved state
    localStorage.setItem('dashboard-collapse-indicators', 'false')
    
    const wrapper = mount(ArtDecoDashboard, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
          'ArtDecoChart': true
        }
      }
    })

    // The component uses ref(getSavedState(...)) which reads from localStorage on init
    // Note: In current ArtDecoDashboard.vue, it uses local getSavedState helper
    // We expect indicatorsExpanded to be false
    expect((wrapper.vm as any).indicatorsExpanded).toBe(false)
  })

  it('should update refresh time correctly', async () => {
    vi.useFakeTimers()
    const wrapper = mount(ArtDecoDashboard, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
          'ArtDecoChart': true
        }
      }
    })

    const initialTime = (wrapper.vm as any).currentTime
    vi.advanceTimersByTime(1000)
    
    // currentTime is updated via setInterval in component
    expect((wrapper.vm as any).currentTime).not.toBe(initialTime)
    vi.useRealTimers()
  })
})
