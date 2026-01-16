/**
 * 统一图表主题配置 - MyStocks数据可视化规范
 *
 * 提供统一的设计语言和视觉风格，确保所有图表的一致性和专业性
 */

import type { EChartsOption } from 'echarts'

// 基础颜色配置
export const BASE_COLORS = {
    primary: '#5470c6',
    success: '#91cc75',
    warning: '#fac858',
    danger: '#ee6666',
    info: '#73c0de',
    secondary: '#3ba272',
    accent: '#fc8452',
    muted: '#9a60b4',
    light: '#ea7ccc',
    dark: '#5470c6'
}

// 金融主题色配置
export const FINANCIAL_COLORS = {
    bullish: '#00C853', // 多头/上涨 - 绿色
    bearish: '#D32F2F', // 空头/下跌 - 红色
    neutral: '#FFC107', // 中性/持平 - 黄色
    volume: '#2196F3', // 成交量 - 蓝色
    average: '#9C27B0', // 均线 - 紫色
    support: '#4CAF50', // 支撑线 - 绿色
    resistance: '#F44336', // 阻力线 - 红色
    background: '#F5F5F5', // 背景色
    grid: '#E0E0E0', // 网格线
    text: '#333333', // 文本色
    mutedText: '#666666' // muted文本
}

// 渐变色配置
export const GRADIENTS = {
    bullish: ['#4CAF50', '#66BB6A', '#81C784'],
    bearish: ['#F44336', '#E57373', '#EF5350'],
    neutral: ['#FFC107', '#FFD54F', '#FFEB3B'],
    volume: ['#2196F3', '#42A5F5', '#64B5F6'],
    heatmap: [
        '#3B4CC0',
        '#5C6BC0',
        '#7986CB',
        '#9FA8DA',
        '#C5CAE9',
        '#EEEEEE',
        '#F8BBD9',
        '#F48FB1',
        '#F06292',
        '#E91E63',
        '#C2185B'
    ]
}

// 字体配置
export const FONT_CONFIG = {
    family: '"Inter", "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
    size: {
        title: 16,
        subtitle: 14,
        axis: 12,
        legend: 12,
        tooltip: 12,
        data: 11
    },
    weight: {
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700
    }
}

// 间距配置
export const SPACING_CONFIG = {
    padding: {
        chart: [20, 20, 20, 20], // 上右下左
        title: [0, 0, 20, 0], // 标题边距
        legend: [20, 0, 0, 0], // 图例边距
        grid: [60, 40, 60, 60] // 网格边距
    },
    margin: {
        series: 4, // 系列间距
        item: 8 // 项目间距
    }
}

// 统一图表主题配置
export const CHART_THEME: EChartsOption = {
    // 颜色方案 - 金融主题
    color: [
        FINANCIAL_COLORS.bullish,
        FINANCIAL_COLORS.bearish,
        FINANCIAL_COLORS.neutral,
        FINANCIAL_COLORS.volume,
        FINANCIAL_COLORS.average,
        BASE_COLORS.info,
        BASE_COLORS.warning,
        BASE_COLORS.secondary,
        BASE_COLORS.accent,
        BASE_COLORS.muted
    ],

    // 背景配置
    backgroundColor: 'transparent',

    // 全局文本样式
    textStyle: {
        fontFamily: FONT_CONFIG.family,
        fontSize: FONT_CONFIG.size.axis,
        color: FINANCIAL_COLORS.text,
        fontWeight: FONT_CONFIG.weight.normal
    },

    // 标题样式
    title: {
        textStyle: {
            fontSize: FONT_CONFIG.size.title,
            fontWeight: FONT_CONFIG.weight.semibold,
            color: FINANCIAL_COLORS.text
        },
        subtextStyle: {
            fontSize: FONT_CONFIG.size.subtitle,
            fontWeight: FONT_CONFIG.weight.normal,
            color: FINANCIAL_COLORS.mutedText
        },
        left: 'center',
        top: 10
    },

    // 图例样式
    legend: {
        textStyle: {
            fontSize: FONT_CONFIG.size.legend,
            color: FINANCIAL_COLORS.mutedText
        },
        itemGap: SPACING_CONFIG.margin.item,
        top: 40
    },

    // 网格配置
    grid: {
        left: SPACING_CONFIG.padding.grid[3],
        right: SPACING_CONFIG.padding.grid[1],
        top: SPACING_CONFIG.padding.grid[0],
        bottom: SPACING_CONFIG.padding.grid[2],
        containLabel: true
    },

    // 坐标轴样式
    xAxis: {
        axisLine: {
            lineStyle: {
                color: FINANCIAL_COLORS.grid
            }
        },
        axisTick: {
            lineStyle: {
                color: FINANCIAL_COLORS.grid
            }
        },
        axisLabel: {
            color: FINANCIAL_COLORS.mutedText,
            fontSize: FONT_CONFIG.size.axis
        },
        splitLine: {
            lineStyle: {
                color: FINANCIAL_COLORS.grid,
                type: 'dashed' as const
            }
        }
    },

    yAxis: {
        axisLine: {
            lineStyle: {
                color: FINANCIAL_COLORS.grid
            }
        },
        axisTick: {
            lineStyle: {
                color: FINANCIAL_COLORS.grid
            }
        },
        axisLabel: {
            color: FINANCIAL_COLORS.mutedText,
            fontSize: FONT_CONFIG.size.axis
        },
        splitLine: {
            lineStyle: {
                color: FINANCIAL_COLORS.grid,
                type: 'dashed' as const
            }
        }
    },

    // 工具提示样式
    tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: FINANCIAL_COLORS.grid,
        borderWidth: 1,
        textStyle: {
            color: FINANCIAL_COLORS.text,
            fontSize: FONT_CONFIG.size.tooltip
        },
        padding: [10, 15],
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        shadowBlur: 10
    },

    // 数据缩放样式
    dataZoom: {
        borderColor: 'transparent',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        handleColor: BASE_COLORS.primary,
        handleSize: '80%',
        fillerColor: 'rgba(84, 112, 198, 0.2)',
        textStyle: {
            color: FINANCIAL_COLORS.mutedText
        }
    },

    // 视觉映射样式
    visualMap: {
        textStyle: {
            color: FINANCIAL_COLORS.mutedText
        },
        inRange: {
            color: GRADIENTS.heatmap
        }
    },

    // 工具箱样式
    toolbox: {
        feature: {
            saveAsImage: {
                title: '保存为图片',
                pixelRatio: 2
            },
            restore: {
                title: '重置'
            },
            dataZoom: {
                title: {
                    zoom: '区域缩放',
                    back: '缩放还原'
                }
            },
            dataView: {
                title: '数据视图',
                readOnly: true
            },
            magicType: {
                title: {
                    line: '切换为折线图',
                    bar: '切换为柱状图',
                    stack: '堆叠',
                    tiled: '平铺'
                }
            }
        },
        iconStyle: {
            borderColor: FINANCIAL_COLORS.grid
        },
        emphasis: {
            iconStyle: {
                borderColor: BASE_COLORS.primary
            }
        }
    }
}

// 暗色主题配置
export const DARK_CHART_THEME: EChartsOption = {
    ...CHART_THEME,

    // 暗色背景
    backgroundColor: '#1a1a1a',

    // 暗色文本
    textStyle: {
        ...CHART_THEME.textStyle,
        color: '#cccccc'
    },

    // 暗色标题
    title: {
        ...CHART_THEME.title,
        textStyle: {
            ...CHART_THEME.title?.textStyle,
            color: '#ffffff'
        },
        subtextStyle: {
            ...CHART_THEME.title?.subtextStyle,
            color: '#cccccc'
        }
    },

    // 暗色图例
    legend: {
        ...CHART_THEME.legend,
        textStyle: {
            ...CHART_THEME.legend?.textStyle,
            color: '#cccccc'
        }
    },

    // 暗色坐标轴
    xAxis: {
        ...CHART_THEME.xAxis,
        axisLine: {
            ...CHART_THEME.xAxis?.axisLine,
            lineStyle: {
                color: '#444444'
            }
        },
        axisTick: {
            ...CHART_THEME.xAxis?.axisTick,
            lineStyle: {
                color: '#444444'
            }
        },
        axisLabel: {
            ...CHART_THEME.xAxis?.axisLabel,
            color: '#cccccc'
        },
        splitLine: {
            ...CHART_THEME.xAxis?.splitLine,
            lineStyle: {
                color: '#333333',
                type: 'dashed' as const
            }
        }
    },

    yAxis: {
        ...CHART_THEME.yAxis,
        axisLine: {
            ...CHART_THEME.yAxis?.axisLine,
            lineStyle: {
                color: '#444444'
            }
        },
        axisTick: {
            ...CHART_THEME.yAxis?.axisTick,
            lineStyle: {
                color: '#444444'
            }
        },
        axisLabel: {
            ...CHART_THEME.yAxis?.axisLabel,
            color: '#cccccc'
        },
        splitLine: {
            ...CHART_THEME.yAxis?.splitLine,
            lineStyle: {
                color: '#333333',
                type: 'dashed' as const
            }
        }
    },

    // 暗色工具提示
    tooltip: {
        ...CHART_THEME.tooltip,
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        borderColor: '#444444',
        textStyle: {
            ...CHART_THEME.tooltip?.textStyle,
            color: '#cccccc'
        }
    },

    // 暗色数据缩放
    dataZoom: {
        ...CHART_THEME.dataZoom,
        backgroundColor: 'rgba(26, 26, 26, 0.8)',
        textStyle: {
            color: '#cccccc'
        }
    }
}

// 紧凑主题（用于小尺寸图表）
export const COMPACT_CHART_THEME: EChartsOption = {
    ...CHART_THEME,

    // 减少内边距
    grid: {
        left: 30,
        right: 20,
        top: 40,
        bottom: 30,
        containLabel: true
    },

    // 更小的字体
    textStyle: {
        ...CHART_THEME.textStyle,
        fontSize: 10
    },

    title: {
        ...CHART_THEME.title,
        textStyle: {
            ...CHART_THEME.title?.textStyle,
            fontSize: 14
        }
    },

    legend: {
        ...CHART_THEME.legend,
        textStyle: {
            ...CHART_THEME.legend?.textStyle,
            fontSize: 10
        }
    },

    xAxis: {
        ...CHART_THEME.xAxis,
        axisLabel: {
            ...CHART_THEME.xAxis?.axisLabel,
            fontSize: 10
        }
    },

    yAxis: {
        ...CHART_THEME.yAxis,
        axisLabel: {
            ...CHART_THEME.yAxis?.axisLabel,
            fontSize: 10
        }
    },

    tooltip: {
        ...CHART_THEME.tooltip,
        textStyle: {
            ...CHART_THEME.tooltip?.textStyle,
            fontSize: 10
        },
        padding: [8, 12]
    }
}

// 移动端主题
export const MOBILE_CHART_THEME: EChartsOption = {
    ...COMPACT_CHART_THEME,

    // 移动端适配
    grid: {
        left: 20,
        right: 20,
        top: 50,
        bottom: 40,
        containLabel: true
    },

    legend: {
        ...COMPACT_CHART_THEME.legend,
        top: 20,
        textStyle: {
            fontSize: 11
        }
    },

    title: {
        ...COMPACT_CHART_THEME.title,
        textStyle: {
            fontSize: 15
        },
        top: 5
    },

    toolbox: {
        ...COMPACT_CHART_THEME.toolbox,
        show: false // 移动端隐藏工具箱
    }
}

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
