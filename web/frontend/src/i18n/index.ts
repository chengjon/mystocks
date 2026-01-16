/**
 * MyStocks 国际化配置
 * Internationalization (i18n) Configuration
 *
 * 支持语言 / Supported Languages:
 * - 中文 (zh-CN) - 默认
 * - 英文 (en-US)
 */

import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

// 支持的语言列表
export const SUPPORTED_LOCALES = [
    { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
    { code: 'en-US', name: 'English', flag: '🇺🇸' }
] as const

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number]['code']

// 默认语言
export const DEFAULT_LOCALE: SupportedLocale = 'zh-CN'

// LocalStorage 键名
export const LOCALE_STORAGE_KEY = 'mystocks-locale'

// 获取初始语言（从 LocalStorage 或浏览器检测）
function getInitialLocale(): SupportedLocale {
    // 1. 尝试从 LocalStorage 读取
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY) as SupportedLocale
    if (stored && SUPPORTED_LOCALES.some(locale => locale.code === stored)) {
        return stored
    }

    // 2. 检测浏览器语言
    const browserLang = navigator.language

    // 中文语言变体
    if (browserLang.startsWith('zh')) {
        return 'zh-CN'
    }

    // 英文语言变体
    if (browserLang.startsWith('en')) {
        return 'en-US'
    }

    // 3. 返回默认语言
    return DEFAULT_LOCALE
}

// 创建 i18n 实例
const i18n = createI18n({
    // 使用 Composition API 模式
    legacy: false,

    // 全局注入 $t
    globalInjection: true,

    // 当前语言
    locale: getInitialLocale(),

    // 回退语言
    fallbackLocale: DEFAULT_LOCALE,

    // 缺失翻译时的处理
    missing: (locale: string, key: string) => {
        if (process.env.NODE_ENV === 'development') {
            console.warn(`[i18n] Missing translation: ${key} for locale: ${locale}`)
        }
        return key
    },

    // 翻译文件
    messages: {
        'zh-CN': zhCN,
        'en-US': enUS
    }
})

// 导出 i18n 实例
export default i18n

// 导出当前语言
export const currentLocale = i18n.global.locale as unknown as SupportedLocale
