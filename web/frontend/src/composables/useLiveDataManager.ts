import { onMounted, onUnmounted, ref } from 'vue'
import { useMenuService } from '@/services/menuService'
import type { MenuItem } from '@/layouts/MenuConfig.enhanced'

/**
 * Live Data Manager Composable
 * Handles WebSocket subscriptions and data updates for the layout
 */
export function useLiveDataManager(menus: MenuItem[]) {
  const { subscribeToLiveUpdates, getLiveUpdateMenus } = useMenuService()
  
  // Track active subscriptions for cleanup
  const activeUnsubscribes = ref<(() => void)[]>([])
  const isConnected = ref(false)
  const lastUpdate = ref<number>(0)

  // Setup subscriptions
  const setup = () => {
    const liveMenus = getLiveUpdateMenus()
    
    // Clear existing
    cleanup()

    liveMenus.forEach(menu => {
      // Create subscription
      const unsubscribe = subscribeToLiveUpdates(menu, (data: any) => {
        // Handle incoming data
        // For now we just log, but this could dispatch to a Pinia store
        // or emit an event bus
        lastUpdate.value = Date.now()
        
        if (import.meta.env.DEV) {
          // console.debug(`[LiveDataManager] Update for ${menu.path}:`, data)
        }
      })
      
      activeUnsubscribes.value.push(unsubscribe)
    })
    
    isConnected.value = true
    console.log(`[LiveDataManager] Setup complete. ${liveMenus.length} channels active.`)
  }

  // Cleanup all subscriptions
  const cleanup = () => {
    activeUnsubscribes.value.forEach(fn => fn())
    activeUnsubscribes.value = []
    isConnected.value = false
  }

  // Lifecycle hooks
  onMounted(() => {
    setup()
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    isConnected,
    lastUpdate,
    setup,
    cleanup
  }
}
