/**
 * User Preferences Pinia Store
 *
 * Global state management for user preferences
 * Wraps useUserPreferences composable for Pinia integration
 */

import { defineStore } from 'pinia'
import { useUserPreferences, type UserPreferences } from '@/composables/useUserPreferences'

export const usePreferencesStore = defineStore('preferences', () => {
  const {
    preferences,
    isLoaded,
    loadPreferences,
    savePreferences,
    updatePreference,
    resetPreferences,
    syncToBackend,
    loadFromBackend
  } = useUserPreferences()

  /**
   * Apply font size to DOM
   * Updates CSS custom property for immediate visual effect (FR-015)
   */
  const applyFontSize = (fontSize: string): void => {
    document.documentElement.style.setProperty('--font-size-base', fontSize)
    updatePreference('fontSize', fontSize)
    console.log(`[PreferencesStore] Font size applied: ${fontSize}`)
  }

  /**
   * Initialize preferences on app startup
   * Loads from LocalStorage and applies font size to DOM
   */
  const initialize = async (): Promise<void> => {
    loadPreferences()

    // Apply saved font size to DOM immediately
    if (preferences.value.fontSize) {
      document.documentElement.style.setProperty('--font-size-base', preferences.value.fontSize)
    }

    console.log('[PreferencesStore] Initialized')
  }

  /**
   * Update page size for a specific table
   */
  const updatePageSize = (table: 'fundFlow' | 'etf' | 'dragonTiger', size: number): void => {
    const key = `pageSize${table.charAt(0).toUpperCase() + table.slice(1)}` as keyof UserPreferences
    updatePreference(key, size)
  }

  /**
   * Update last visited watchlist tab
   */
  const updateLastWatchlistTab = (tab: string): void => {
    updatePreference('lastWatchlistTab', tab)
  }

  /**
   * Update last Wencai query
   */
  const updateWencaiLastQuery = (query: string | null): void => {
    updatePreference('wencaiLastQuery', query)
  }

  return {
    // State
    preferences,
    isLoaded,

    // Actions
    loadPreferences,
    savePreferences,
    updatePreference,
    resetPreferences,
    syncToBackend,
    loadFromBackend,
    initialize,

    // Specific updaters for type safety
    applyFontSize,
    updatePageSize,
    updateLastWatchlistTab,
    updateWencaiLastQuery
  }
})
