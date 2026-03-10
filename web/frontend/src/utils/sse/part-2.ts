
/**
 * SSE Connection for Vue Composition API
 *
 * Note: This is a framework-agnostic utility. For Vue 3 integration,
 * use the SSEConnection class directly or create a Vue composable wrapper.
 *
 * Example Vue composable:
 * ```typescript
 * import { ref, onUnmounted } from 'vue'
 * import { SSEManager, type SSEOptions, type SSEEvent } from '@/utils/sse.ts'
 *
 * export function useSSE(name: string, options: SSEOptions) {
 *   const connection = SSEManager.getInstance().create(name, options)
 *   const state = ref(connection.getState())
 *   const eventHandlers = new Map<string, Set<(event: SSEEvent) => void>>()
 *
 *   const unsubscribe = connection.onStateChange((newState) => {
 *     state.value = newState
 *   })
 *
 *   onUnmounted(() => {
 *     unsubscribe()
 *     SSEManager.getInstance().close(name)
 *   })
 *
 *   return {
 *     state: state.value,
 *     subscribe: (eventType: string, handler: (event: SSEEvent) => void) =>
 *       connection.subscribe(eventType, handler)
 *   }
 * }
 * ```
 */

import { SSEManager, SSEConnection, type SSEOptions } from './part-1.ts'

export function useSSE(name: string, options: SSEOptions): SSEConnection {
  // This function is now a placeholder. See the documentation above
  // for how to create a Vue composable wrapper.
  console.warn('useSSE: This is a placeholder. Please implement a Vue composable wrapper.')
  return SSEManager.getInstance().create(name, options)
}

export default SSEConnection
