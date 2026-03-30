// web/frontend/src/composables/useWebSocket.ts
import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const message = ref<unknown | null>(null)
  const error = ref<Event | null>(null)

  const connect = (url: string) => {
    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      isConnected.value = true
    }

    ws.value.onmessage = (event) => {
      try {
        message.value = JSON.parse(event.data)
      } catch (_e) {
        message.value = event.data
      }
    }

    ws.value.onerror = (event) => {
      error.value = event
      console.error('WebSocket error:', event)
    }

    ws.value.onclose = () => {
      isConnected.value = false
    }
  }

  const disconnect = () => {
    if (ws.value && isConnected.value) {
      ws.value.close()
    }
  }

  const send = (data: unknown) => {
    if (ws.value && isConnected.value) {
      ws.value.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected.')
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    message,
    error,
    connect,
    disconnect,
    send,
  }
}
