/**
 * Linear Theme Manager
 * Manages Linear/Modern design system theme switching and CSS variable injection
 */

import { ref, computed, type Ref } from 'vue'

export interface ThemeConfig {
  name: string
  mode: 'dark' | 'light'
  version: string
  colors: {
    background: Record<string, string>
    foreground: Record<string, string>
    accent: Record<string, string>
    border: Record<string, string>
    gradient: Record<string, string>
  }
  backgroundLayers: {
    baseGradient: string
    noiseOpacity: number
    gridOpacity: number
    gridSize: number
    blobs: Array<{
      position: string
      size: string
      blur: number
      color: string
      animationDuration: number
      pulse?: boolean
    }>
  }
  shadows: Record<string, string>
  typography: {
    fontFamily: Record<string, string>
    scale: Record<string, any>
  }
  spacing: Record<string, string>
  radius: Record<string, string>
  animation: {
    duration: Record<string, string>
    easing: Record<string, string>
    float: { from: any; to: any }
  }
  spotlight: {
    size: number
    opacity: number
    blur: number
  }
  components: Record<string, any>
  metadata: Record<string, any>
}

const THEME_STORAGE_KEY = 'linear-theme-preference'

// Import theme configs
import linearDarkTheme from './themes/linear-dark.json'
import linearLightTheme from './themes/linear-light.json'

class ThemeManagerImpl {
  private currentTheme = ref<ThemeConfig>(linearDarkTheme as ThemeConfig)
  private isInitialized = false

  constructor() {
    this.loadSavedTheme()
  }

  /**
   * Load saved theme from localStorage
   */
  private loadSavedTheme() {
    if (typeof window === 'undefined') return

    try {
      const savedMode = localStorage.getItem(THEME_STORAGE_KEY) as 'dark' | 'light' | null
      if (savedMode === 'light') {
        this.currentTheme.value = linearLightTheme as ThemeConfig
      } else {
        this.currentTheme.value = linearDarkTheme as ThemeConfig
      }
    } catch (error) {
      console.warn('[Linear ThemeManager] Failed to load saved theme:', error)
    }
  }

  /**
   * Save theme to localStorage
   */
  private saveTheme(mode: 'dark' | 'light') {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem(THEME_STORAGE_KEY, mode)
    } catch (error) {
      console.warn('[Linear ThemeManager] Failed to save theme:', error)
    }
  }

  /**
   * Apply Linear theme CSS variables to DOM
   */
  private applyTheme(theme: ThemeConfig) {
    if (typeof document === 'undefined') return

    const root = document.documentElement

    // Apply background colors
    Object.entries(theme.colors.background).forEach(([key, value]) => {
      root.style.setProperty(`--bg-${key}`, value)
    })

    // Apply foreground colors
    Object.entries(theme.colors.foreground).forEach(([key, value]) => {
      root.style.setProperty(`--fg-${key}`, value)
    })

    // Apply accent colors
    Object.entries(theme.colors.accent).forEach(([key, value]) => {
      root.style.setProperty(`--accent-${key}`, value)
    })

    // Apply border colors
    Object.entries(theme.colors.border).forEach(([key, value]) => {
      root.style.setProperty(`--border-${key}`, value)
    })

    // Apply gradients
    Object.entries(theme.colors.gradient).forEach(([key, value]) => {
      root.style.setProperty(`--gradient-${key}`, value)
    })

    // Apply background layer settings
    root.style.setProperty('--bg-base-gradient', theme.backgroundLayers.baseGradient)
    root.style.setProperty('--bg-noise-opacity', theme.backgroundLayers.noiseOpacity.toString())
    root.style.setProperty('--bg-grid-opacity', theme.backgroundLayers.gridOpacity.toString())
    root.style.setProperty('--bg-grid-size', theme.backgroundLayers.gridSize + 'px')

    // Apply shadows
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value)
    })

    // Apply typography
    root.style.setProperty('--font-sans', theme.typography.fontFamily.sans)
    root.style.setProperty('--font-mono', theme.typography.fontFamily.mono)

    // Apply spacing
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value)
    })

    // Apply radius
    Object.entries(theme.radius).forEach(([key, value]) => {
      root.style.setProperty(`--radius-${key}`, value)
    })

    // Apply animation settings
    root.style.setProperty('--duration-fast', theme.animation.duration.fast)
    root.style.setProperty('--duration-normal', theme.animation.duration.normal)
    root.style.setProperty('--duration-slow', theme.animation.duration.slow)
    root.style.setProperty('--duration-blob', theme.animation.duration.blob)
    root.style.setProperty('--easing-default', theme.animation.easing.default)
    root.style.setProperty('--easing-out', theme.animation.easing.out)
    root.style.setProperty('--easing-in-out', theme.animation.easing.inOut)

    // Apply spotlight settings
    root.style.setProperty('--spotlight-size', theme.spotlight.size + 'px')
    root.style.setProperty('--spotlight-opacity', theme.spotlight.opacity.toString())
    root.style.setProperty('--spotlight-blur', theme.spotlight.blur + 'px')

    // Set data attribute for theme mode
    root.setAttribute('data-theme', theme.mode)
  }

  /**
   * Initialize theme system (call once on app mount)
   */
  init() {
    if (this.isInitialized) return

    this.applyTheme(this.currentTheme.value)
    this.isInitialized = true
    console.log(`✅ Linear theme initialized: ${this.currentTheme.value.name}`)
  }

  /**
   * Get current theme
   */
  getTheme() {
    return this.currentTheme
  }

  /**
   * Get current theme as computed
   */
  getThemeComputed() {
    return computed(() => this.currentTheme.value)
  }

  /**
   * Check if current theme is dark
   */
  isDark() {
    return computed(() => this.currentTheme.value.mode === 'dark')
  }

  /**
   * Check if current theme is light
   */
  isLight() {
    return computed(() => this.currentTheme.value.mode === 'light')
  }

  /**
   * Switch to light theme
   */
  setLightTheme() {
    this.currentTheme.value = linearLightTheme as ThemeConfig
    this.applyTheme(this.currentTheme.value)
    this.saveTheme('light')
  }

  /**
   * Switch to dark theme
   */
  setDarkTheme() {
    this.currentTheme.value = linearDarkTheme as ThemeConfig
    this.applyTheme(this.currentTheme.value)
    this.saveTheme('dark')
  }

  /**
   * Toggle between light and dark themes
   */
  toggleTheme() {
    if (this.currentTheme.value.mode === 'light') {
      this.setDarkTheme()
    } else {
      this.setLightTheme()
    }
  }

  /**
   * Get theme value by path
   */
  get(path: string): any {
    const keys = path.split('.')
    let value: any = this.currentTheme.value

    for (const key of keys) {
      value = value?.[key]
    }

    return value
  }
}

// Singleton instance
export const themeManager = new ThemeManagerImpl()

// Composable for using theme in components
export function useTheme() {
  return {
    theme: themeManager.getThemeComputed(),
    isDark: themeManager.isDark(),
    isLight: themeManager.isLight(),
    setLightTheme: () => themeManager.setLightTheme(),
    setDarkTheme: () => themeManager.setDarkTheme(),
    toggleTheme: () => themeManager.toggleTheme(),
    get: (path: string) => themeManager.get(path)
  }
}

export default themeManager
