import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const PREF_STORAGE_KEY = 'artdeco-preferences'

interface UserPreferences {
  theme: 'dark' | 'light' | 'system'
  sidebarCollapsed: boolean
  reducedMotion: boolean
  showPerformance: boolean
  chartRefreshRate: number // ms
}

const defaultPreferences: UserPreferences = {
  theme: 'dark',
  sidebarCollapsed: false,
  reducedMotion: false,
  showPerformance: false,
  chartRefreshRate: 3000
}

export const usePreferenceStore = defineStore('artdeco-preferences', () => {
  // State
  const theme = ref<UserPreferences['theme']>(defaultPreferences.theme)
  const sidebarCollapsed = ref(defaultPreferences.sidebarCollapsed)
  const reducedMotion = ref(defaultPreferences.reducedMotion)
  const showPerformance = ref(defaultPreferences.showPerformance)
  const chartRefreshRate = ref(defaultPreferences.chartRefreshRate)

  // Actions
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    applyTheme()
  }

  const setTheme = (newTheme: UserPreferences['theme']) => {
    theme.value = newTheme
    applyTheme()
  }

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const togglePerformance = () => {
    showPerformance.value = !showPerformance.value
  }

  const applyTheme = () => {
    const root = document.documentElement
    if (theme.value === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.setAttribute('data-theme', isDark ? 'dark' : 'light')
    } else {
      root.setAttribute('data-theme', theme.value)
    }
  }

  // Persistence
  const load = () => {
    const stored = localStorage.getItem(PREF_STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        theme.value = parsed.theme ?? defaultPreferences.theme
        sidebarCollapsed.value = parsed.sidebarCollapsed ?? defaultPreferences.sidebarCollapsed
        reducedMotion.value = parsed.reducedMotion ?? defaultPreferences.reducedMotion
        showPerformance.value = parsed.showPerformance ?? defaultPreferences.showPerformance
        chartRefreshRate.value = parsed.chartRefreshRate ?? defaultPreferences.chartRefreshRate
      } catch (e) {
        console.error('Failed to load preferences', e)
      }
    }
    applyTheme()
  }

  const save = () => {
    const state: UserPreferences = {
      theme: theme.value,
      sidebarCollapsed: sidebarCollapsed.value,
      reducedMotion: reducedMotion.value,
      showPerformance: showPerformance.value,
      chartRefreshRate: chartRefreshRate.value
    }
    localStorage.setItem(PREF_STORAGE_KEY, JSON.stringify(state))
  }

  // Watchers
  watch([theme, sidebarCollapsed, reducedMotion, showPerformance, chartRefreshRate], () => {
    save()
  })

  // Init
  load()

  return {
    theme,
    sidebarCollapsed,
    reducedMotion,
    showPerformance,
    chartRefreshRate,
    toggleTheme,
    setTheme,
    toggleSidebar,
    togglePerformance
  }
})
