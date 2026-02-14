/**
 * 统一图表主题配置 - MyStocks数据可视化规范
 *
 * 提供统一的设计语言和视觉风格，确保所有图表的一致性和专业性
 */

import type { EChartsOption } from 'echarts'

// 导出便捷函数
export const getChartTheme = (
    variant: 'default' | 'dark' | 'compact' | 'mobile' = 'default',
    customOptions?: EChartsOption
): EChartsOption => {
    let baseTheme: EChartsOption

    switch (variant) {
        case 'dark':
            baseTheme = DARK_CHART_THEME
            break
        case 'compact':
            baseTheme = COMPACT_CHART_THEME
            break
        case 'mobile':
            baseTheme = MOBILE_CHART_THEME
            break
        default:
            baseTheme = CHART_THEME
    }

    // 合并自定义选项
    return customOptions ? { ...baseTheme, ...customOptions } : baseTheme
}

// 自动检测并返回合适的主题
export const getAdaptiveTheme = (customOptions?: EChartsOption): EChartsOption => {
    // 检测是否为移动设备
    const isMobile = window.innerWidth < 768

    // 检测系统主题偏好
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    if (isMobile) {
        return getChartTheme('mobile', customOptions)
    } else if (prefersDark) {
        return getChartTheme('dark', customOptions)
    } else {
        return getChartTheme('default', customOptions)
    }
}

// 默认导出
export default CHART_THEME

