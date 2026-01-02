/**
 * Theme Manager
 *
 * 主题管理器，提供亮色/暗色主题切换功能
 */

import { ref, computed } from 'vue'

// 主题模式类型
export type ThemeMode = 'light' | 'dark'

// 当前主题状态（响应式）
const currentMode = ref<ThemeMode>('dark')

// 主题配置
const themes = {
  light: {
    primary: '#3b82f6',
    background: '#ffffff',
    foreground: '#000000',
    card: '#f3f4f6',
    border: '#e5e7eb'
  },
  dark: {
    primary: '#60a5fa',
    background: '#0f172a',
    foreground: '#f8fafc',
    card: '#1e293b',
    border: '#334155'
  }
}

/**
 * Theme Manager 类
 */
class ThemeManager {
  /**
   * 初始化主题
   */
  init() {
    // 从localStorage读取保存的主题
    const savedTheme = localStorage.getItem('theme-mode') as ThemeMode | null

    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      currentMode.value = savedTheme
    } else {
      // 检测系统主题偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      currentMode.value = prefersDark ? 'dark' : 'light'
    }

    // 应用主题到DOM
    this.applyTheme(currentMode.value)
  }

  /**
   * 获取当前主题的计算属性
   */
  getThemeComputed() {
    return {
      mode: computed(() => currentMode.value),
      isDark: computed(() => currentMode.value === 'dark'),
      isLight: computed(() => currentMode.value === 'light')
    }
  }

  /**
   * 切换主题
   */
  toggleTheme() {
    const newMode: ThemeMode = currentMode.value === 'dark' ? 'light' : 'dark'
    this.setTheme(newMode)
  }

  /**
   * 设置主题
   */
  setTheme(mode: ThemeMode) {
    currentMode.value = mode
    localStorage.setItem('theme-mode', mode)
    this.applyTheme(mode)
  }

  /**
   * 获取当前主题
   */
  getTheme(): ThemeMode {
    return currentMode.value
  }

  /**
   * 应用主题到DOM
   */
  private applyTheme(mode: ThemeMode) {
    const root = document.documentElement

    // 移除旧的主题类
    root.classList.remove('theme-light', 'theme-dark')

    // 添加新的主题类
    root.classList.add(`theme-${mode}`)

    // 设置CSS变量
    const theme = themes[mode]
    root.style.setProperty('--theme-primary', theme.primary)
    root.style.setProperty('--theme-background', theme.background)
    root.style.setProperty('--theme-foreground', theme.foreground)
    root.style.setProperty('--theme-card', theme.card)
    root.style.setProperty('--theme-border', theme.border)
  }
}

// 创建单例实例
const themeManager = new ThemeManager()

/**
 * Vue composable: useTheme
 *
 * 提供响应式的主题切换API
 */
export function useTheme() {
  const isDark = computed(() => currentMode.value === 'dark')
  const isLight = computed(() => currentMode.value === 'light')
  const theme = computed(() => currentMode.value)

  const toggleTheme = () => {
    themeManager.toggleTheme()
  }

  const setTheme = (mode: ThemeMode) => {
    themeManager.setTheme(mode)
  }

  return {
    isDark,
    isLight,
    theme,
    toggleTheme,
    setTheme
  }
}

// 导出单例实例（默认导出）
export default themeManager
