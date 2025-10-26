/**
 * User Preferences Composable
 *
 * Manages user preferences with LocalStorage persistence (FR-019)
 * Supports optional backend sync for multi-device consistency
 */

import { ref, watch } from 'vue'

export interface UserPreferences {
  fontSize: string
  pageSizeFundFlow: number
  pageSizeETF: number
  pageSizeDragonTiger: number
  lastWatchlistTab: string
  wencaiLastQuery: string | null
}

const defaultPreferences: UserPreferences = {
  fontSize: '16px',
  pageSizeFundFlow: 20,
  pageSizeETF: 20,
  pageSizeDragonTiger: 20,
  lastWatchlistTab: 'user',
  wencaiLastQuery: null
}

const STORAGE_KEY = 'userPreferences'
const STORAGE_VERSION = '1.0'

export function useUserPreferences() {
  const preferences = ref<UserPreferences>({ ...defaultPreferences })
  const isLoaded = ref(false)
  const saveTimeout = ref<number | null>(null)

  /**
   * Load preferences from LocalStorage
   * Merges with defaults to handle new settings
   */
  const loadPreferences = (): void => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)

        // Validate version and merge with defaults
        if (parsed.version === STORAGE_VERSION) {
          preferences.value = { ...defaultPreferences, ...parsed.preferences }
        } else {
          // Migration logic for version changes
          console.warn('[Preferences] Version mismatch, using defaults')
          preferences.value = { ...defaultPreferences }
        }
      }

      isLoaded.value = true
      console.log('[Preferences] Loaded:', preferences.value)
    } catch (error) {
      console.error('[Preferences] Failed to load:', error)
      preferences.value = { ...defaultPreferences }
      isLoaded.value = true
    }
  }

  /**
   * Save preferences to LocalStorage
   * Includes error handling for quota exceeded
   */
  const savePreferences = (): void => {
    try {
      const data = {
        version: STORAGE_VERSION,
        preferences: preferences.value,
        lastUpdated: new Date().toISOString()
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
      console.log('[Preferences] Saved:', preferences.value)
    } catch (error) {
      console.error('[Preferences] Failed to save:', error)

      // Fallback: Try sessionStorage if quota exceeded
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        try {
          sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
            version: STORAGE_VERSION,
            preferences: preferences.value
          }))
          console.warn('[Preferences] Saved to sessionStorage (quota exceeded)')
        } catch (sessionError) {
          console.error('[Preferences] SessionStorage also failed:', sessionError)
        }
      }
    }
  }

  /**
   * Update a single preference key
   * @param key - Preference key to update
   * @param value - New value
   */
  const updatePreference = <K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ): void => {
    preferences.value[key] = value

    // Debounced save (500ms delay)
    if (saveTimeout.value) {
      clearTimeout(saveTimeout.value)
    }

    saveTimeout.value = window.setTimeout(() => {
      savePreferences()
    }, 500)
  }

  /**
   * Reset all preferences to defaults
   */
  const resetPreferences = (): void => {
    preferences.value = { ...defaultPreferences }
    savePreferences()
    console.log('[Preferences] Reset to defaults')
  }

  /**
   * Optional: Sync preferences to backend
   * Non-critical operation, fails gracefully
   */
  const syncToBackend = async (): Promise<void> => {
    try {
      const response = await fetch('/api/user/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add auth token from your auth system
          // 'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(preferences.value)
      })

      if (response.ok) {
        console.log('[Preferences] Synced to backend')
      }
    } catch (error) {
      // Non-critical failure, log only
      console.warn('[Preferences] Backend sync failed (non-critical):', error)
    }
  }

  /**
   * Optional: Load preferences from backend
   * Falls back to LocalStorage if unavailable
   */
  const loadFromBackend = async (): Promise<void> => {
    try {
      const response = await fetch('/api/user/preferences', {
        headers: {
          // Add auth token from your auth system
          // 'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.preferences) {
          preferences.value = { ...defaultPreferences, ...data.preferences }
          savePreferences() // Save to LocalStorage as cache
          console.log('[Preferences] Loaded from backend')
        }
      }
    } catch (error) {
      console.warn('[Preferences] Backend load failed, using LocalStorage:', error)
      loadPreferences() // Fallback to LocalStorage
    }
  }

  // Auto-save on changes (with debounce)
  watch(preferences, () => {
    if (isLoaded.value && saveTimeout.value) {
      // Debouncing is handled in updatePreference
      // This watch ensures manual changes also trigger save
    }
  }, { deep: true })

  // Initialize on first use
  if (!isLoaded.value) {
    loadPreferences()
  }

  return {
    preferences,
    isLoaded,
    loadPreferences,
    savePreferences,
    updatePreference,
    resetPreferences,
    syncToBackend,
    loadFromBackend
  }
}
