/**
 * useI18n Composable
 *
 * 国际化辅助函数集合，封装 vue-i18n 的常用功能
 * Internationalization helper functions wrapping vue-i18n
 *
 * 特性 / Features:
 * - 语言切换 / Language switching
 * - 日期本地化 / Date localization
 * - 数字本地化 / Number localization
 * - 货币本地化 / Currency localization
 * - LocalStorage 持久化 / Persistent storage
 */

import { computed, watch } from 'vue'
import { useI18n as useVueI18n } from 'vue-i18n'
import { SUPPORTED_LOCALES, DEFAULT_LOCALE, LOCALE_STORAGE_KEY, type SupportedLocale } from '@/i18n'

/**
 * 国际化 Composable
 */
export function useI18n() {
    const { t, locale, _availableLocales } = useVueI18n()

    /**
     * 当前语言（只读）
     */
    const currentLocale = computed(() => locale.value as SupportedLocale)

    /**
     * 当前语言信息
     */
    const currentLocaleInfo = computed(() => {
        return (
            SUPPORTED_LOCALES.find(l => l.code === locale.value) || {
                code: DEFAULT_LOCALE,
                name: '简体中文',
                flag: '🇨🇳'
            }
        )
    })

    /**
     * 支持的语言列表
     */
    const supportedLocales = computed(() => SUPPORTED_LOCALES)

    /**
     * 切换语言
     * @param newLocale 新语言代码
     */
    const setLocale = (newLocale: SupportedLocale) => {
        if (!SUPPORTED_LOCALES.some(l => l.code === newLocale)) {
            console.error(`[useI18n] Unsupported locale: ${newLocale}`)
            return
        }

        locale.value = newLocale
        localStorage.setItem(LOCALE_STORAGE_KEY, newLocale)

        // 更新 HTML lang 属性
        document.documentElement.lang = newLocale
    }

    /**
     * 切换到下一个语言（循环切换）
     */
    const toggleLocale = () => {
        const currentIndex = SUPPORTED_LOCALES.findIndex(l => l.code === locale.value)
        const nextIndex = (currentIndex + 1) % SUPPORTED_LOCALES.length
        setLocale(SUPPORTED_LOCALES[nextIndex].code as SupportedLocale)
    }

    /**
     * 翻译函数（带命名空间支持）
     * @param key 翻译键
     * @param params 参数
     */
    const translate = (key: string, params?: Record<string, unknown>) => {
        return t(key, params || {})
    }

    /**
     * 日期本地化
     * @param date 日期对象或字符串
     * @param options 格式化选项
     */
    const formatDate = (date: Date | string, options?: Intl.DateTimeFormatOptions): string => {
        const dateObj = typeof date === 'string' ? new Date(date) : date
        return new Intl.DateTimeFormat(locale.value, options).format(dateObj)
    }

    /**
     * 数字本地化
     * @param value 数字值
     * @param options 格式化选项
     */
    const formatNumber = (value: number, options?: Intl.NumberFormatOptions): string => {
        return new Intl.NumberFormat(locale.value, options).format(value)
    }

    /**
     * 货币本地化
     * @param value 金额
     * @param currency 货币代码（默认：CNY/USD 根据语言）
     */
    const formatCurrency = (value: number, currency?: string): string => {
        // 根据语言自动选择货币
        const defaultCurrency = locale.value === 'zh-CN' ? 'CNY' : 'USD'
        const targetCurrency = currency || defaultCurrency

        return new Intl.NumberFormat(locale.value, {
            style: 'currency',
            currency: targetCurrency
        }).format(value)
    }

    /**
     * 百分比本地化
     * @param value 数值（0-1 或 0-100）
     * @param decimals 小数位数
     */
    const formatPercent = (value: number, decimals: number = 2): string => {
        // 如果值 > 1，假设已经是百分比形式
        const normalizedValue = value > 1 ? value / 100 : value

        return new Intl.NumberFormat(locale.value, {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(normalizedValue)
    }

    /**
     * 股票价格格式化（中国A股：红色涨绿色跌）
     * @param value 价格值
     * @param decimals 小数位数
     */
    const formatStockPrice = (value: number, decimals: number = 2): string => {
        return formatNumber(value, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        })
    }

    /**
     * 涨跌幅格式化（带符号和颜色提示）
     * @param value 涨跌幅值（如 0.0523 表示 +5.23%）
     * @param decimals 小数位数
     */
    const formatChange = (value: number, decimals: number = 2): string => {
        const sign = value > 0 ? '+' : ''
        return `${sign}${formatPercent(value, decimals)}`
    }

    /**
     * 相对时间格式化（如"3小时前"）
     * @param date 日期
     */
    const formatRelativeTime = (date: Date | string): string => {
        const dateObj = typeof date === 'string' ? new Date(date) : date
        const now = new Date()
        const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000)

        const rtf = new Intl.RelativeTimeFormat(locale.value, { numeric: 'auto' })

        // 小于 1 分钟
        if (diffInSeconds < 60) {
            return rtf.format(-diffInSeconds, 'second')
        }

        // 小于 1 小时
        const diffInMinutes = Math.floor(diffInSeconds / 60)
        if (diffInMinutes < 60) {
            return rtf.format(-diffInMinutes, 'minute')
        }

        // 小于 1 天
        const diffInHours = Math.floor(diffInMinutes / 60)
        if (diffInHours < 24) {
            return rtf.format(-diffInHours, 'hour')
        }

        // 小于 1 个月
        const diffInDays = Math.floor(diffInHours / 24)
        if (diffInDays < 30) {
            return rtf.format(-diffInDays, 'day')
        }

        // 小于 1 年
        const diffInMonths = Math.floor(diffInDays / 30)
        if (diffInMonths < 12) {
            return rtf.format(-diffInMonths, 'month')
        }

        // 超过 1 年
        const diffInYears = Math.floor(diffInMonths / 12)
        return rtf.format(-diffInYears, 'year')
    }

    /**
     * 大数字格式化（如 1.2K, 1.5M）
     * @param value 数值
     */
    const formatCompactNumber = (value: number): string => {
        return new Intl.NumberFormat(locale.value, {
            notation: 'compact',
            compactDisplay: 'short'
        }).format(value)
    }

    /**
     * 文件大小格式化
     * @param bytes 字节数
     */
    const formatBytes = (bytes: number): string => {
        const units = locale.value === 'zh-CN' ? ['B', 'KB', 'MB', 'GB', 'TB'] : ['B', 'KB', 'MB', 'GB', 'TB']

        let size = bytes
        let unitIndex = 0

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024
            unitIndex++
        }

        return `${formatNumber(size, { maximumFractionDigits: 2 })} ${units[unitIndex]}`
    }

    /**
     * 批量翻译（用于表格列头等）
     * @param keys 翻译键数组
     */
    const translateBatch = (keys: string[]): Record<string, string> => {
        return keys.reduce(
            (acc, key) => {
                acc[key] = t(key)
                return acc
            },
            {} as Record<string, string>
        )
    }

    // 监听语言变化，自动更新 HTML lang 属性
    watch(
        locale,
        newLocale => {
            document.documentElement.lang = newLocale
        },
        { immediate: true }
    )

    return {
        // 核心 API
        t: translate,
        locale: currentLocale,
        localeInfo: currentLocaleInfo,
        supportedLocales,

        // 语言切换
        setLocale,
        toggleLocale,

        // 格式化函数
        formatDate,
        formatNumber,
        formatCurrency,
        formatPercent,
        formatStockPrice,
        formatChange,
        formatRelativeTime,
        formatCompactNumber,
        formatBytes,

        // 批量操作
        translateBatch
    }
}

/**
 * 导出类型
 */
export type LocaleInfo = {
    code: SupportedLocale
    name: string
    flag: string
}
