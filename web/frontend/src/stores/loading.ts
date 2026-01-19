import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLoadingStore = defineStore('loading', () => {
  // State
  const globalLoading = ref(false)
  const loadingStates = ref<Record<string, boolean>>({})

  // Actions
  const setGlobalLoading = (loading: boolean) => {
    globalLoading.value = loading
  }

  const setLoading = (key: string, loading: boolean) => {
    loadingStates.value[key] = loading
  }

  const isLoading = (key?: string) => {
    if (key) {
      return loadingStates.value[key] || false
    }
    return globalLoading.value
  }

  const clearLoading = (key: string) => {
    delete loadingStates.value[key]
  }

  const clearAllLoading = () => {
    loadingStates.value = {}
    globalLoading.value = false
  }

  return {
    // State
    globalLoading,
    loadingStates,

    // Actions
    setGlobalLoading,
    setLoading,
    isLoading,
    clearLoading,
    clearAllLoading
  }
})
