<template>
    <div class="advanced-heatmap-container">
        <div class="chart-header" v-if="title">
            <h3 class="chart-title">{{ title }}</h3>
            <div class="chart-toolbar">
                <el-select v-model="colorScheme" size="small" @change="updateColorScheme" style="width: 120px">
                    <el-option label="金融配色" value="financial" />
                    <el-option label="经典配色" value="classic" />
                    <el-option label="冷暖配色" value="coolwarm" />
                </el-select>

                <el-tooltip content="切换视图模式" placement="top">
                    <el-button size="small" @click="toggleViewMode">
                        <el-icon><View /></el-icon>
                    </el-button>
                </el-tooltip>

                <el-button size="small" @click="resetZoom">
                    <el-icon><Refresh /></el-icon>
                    重置
                </el-button>

                <el-button size="small" @click="exportChart" :loading="exporting">
                    <el-icon><Download /></el-icon>
                    导出
                </el-button>
            </div>
        </div>

        <div class="chart-stats" v-if="showStats">
            <div class="stat-item">
                <span class="stat-label">最大值:</span>
                <span class="stat-value">{{ formatNumber(maxValue) }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">最小值:</span>
                <span class="stat-value">{{ formatNumber(minValue) }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">平均值:</span>
                <span class="stat-value">{{ formatNumber(avgValue) }}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">数据点:</span>
                <span class="stat-value">{{ totalPoints }}</span>
            </div>
        </div>

        <div ref="chartRef" :style="{ width: width, height: height }"></div>

        <div class="chart-loading" v-if="loading">
            <el-icon class="is-loading">
                <Loading />
            </el-icon>
            <span>渲染热力图...</span>
        </div>

        <div class="chart-error" v-if="error">
            <el-alert :title="error" type="error" :closable="false" show-icon />
            <el-button @click="retry" size="small">重试</el-button>
        </div>

        <div class="chart-tooltip" v-if="showTooltip && tooltipData" v-show="tooltipVisible">
            <div class="tooltip-header">{{ tooltipData.xLabel }} × {{ tooltipData.yLabel }}</div>
            <div class="tooltip-value">{{ formatNumber(tooltipData.value) }}</div>
            <div class="tooltip-percentage" v-if="tooltipData.percentage">
                占比较: {{ tooltipData.percentage.toFixed(1) }}%
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import { View, Refresh, Download, Loading } from '@element-plus/icons-vue'

    const props = defineProps({
        data: {
            type: Array,
            default: () => []
        },
        xAxis: {
            type: Array,
            default: () => []
        },
        yAxis: {
            type: Array,
            default: () => []
        },
        title: {
            type: String,
            default: ''
        },
        width: {
            type: String,
            default: '100%'
        },
        height: {
            type: String,
            default: '400px'
        },
        showStats: {
            type: Boolean,
            default: true
        },
        colorScheme: {
            type: String,
            default: 'financial',
            validator: value => ['financial', 'classic', 'coolwarm'].includes(value)
        },
        minValue: {
            type: Number,
            default: undefined
        },
        maxValue: {
            type: Number,
            default: undefined
        },
        valueFormatter: {
            type: Function,
            default: value => value.toString()
        }
    })

    const emit = defineEmits(['cell-click', 'ready', 'error'])

    const chartRef = ref()
    let chartInstance = null
    const loading = ref(false)
    const error = ref('')
    const exporting = ref(false)
    const colorScheme = ref(props.colorScheme)
    const showTooltip = ref(true)
    const tooltipVisible = ref(false)
    const tooltipData = ref(null)

    // 计算数据统计
    const dataStats = computed(() => {
        const flatData = props.data.flat().filter(val => val !== null && val !== undefined)
        if (flatData.length === 0) return { min: 0, max: 0, avg: 0, total: 0 }

        const min = props.minValue ?? Math.min(...flatData)
        const max = props.maxValue ?? Math.max(...flatData)
        const avg = flatData.reduce((a, b) => a + b, 0) / flatData.length
        const total = flatData.length

        return { min, max, avg, total }
    })

    const maxValue = computed(() => dataStats.value.max)
    const minValue = computed(() => dataStats.value.min)
    const avgValue = computed(() => dataStats.value.avg)
    const totalPoints = computed(() => dataStats.value.total)

    // 颜色方案配置
    const colorSchemes = {
        financial: GRADIENTS.heatmap,
        classic: [
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
        ],
        coolwarm: [
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

    // 初始化图表
    const initChart = async () => {
        if (!chartRef.value || !props.data.length) return

        try {
            loading.value = true
            error.value = ''

            // 销毁旧实例
            if (chartInstance) {
                chartInstance.dispose()
            }

            // 创建新实例
             chartInstance = echarts.init(chartRef.value, artDecoTheme)

            // 图表配置
            const option = {
                title: props.title
                    ? {
                          text: props.title,
                          left: 'center',
                          textStyle: {
                              fontSize: 16,
                              fontWeight: '600'
                          }
                      }
                    : undefined,

                tooltip: {
                    trigger: 'item',
                    axisPointer: {
                        type: 'cross'
                    },
                    formatter: params => {
                        const xIndex = params.data[0]
                        const yIndex = params.data[1]
                        const value = params.data[2]
                        const xLabel = props.xAxis[xIndex] || `X${xIndex}`
                        const yLabel = props.yAxis[yIndex] || `Y${yIndex}`

                        // 计算百分比
                        const percentage = maxValue.value > 0 ? (value / maxValue.value) * 100 : 0

                        // 更新tooltip数据
                        tooltipData.value = {
                            xLabel,
                            yLabel,
                            value,
                            percentage
                        }
                        tooltipVisible.value = true

                        return `
            <strong>${xLabel} × ${yLabel}</strong><br/>
            值: ${props.valueFormatter(value)}<br/>
            占比较: ${percentage.toFixed(1)}%
          `
                    }
                },

                grid: {
                    height: '70%',
                    top: props.title ? '15%' : '10%',
                    bottom: '20%'
                },

                xAxis: {
                    type: 'category',
                    data: props.xAxis,
                    splitArea: {
                        show: true
                    },
                    axisLabel: {
                        rotate: props.xAxis.length > 10 ? 45 : 0,
                        fontSize: 11
                    }
                },

                yAxis: {
                    type: 'category',
                    data: props.yAxis,
                    splitArea: {
                        show: true
                    },
                    axisLabel: {
                        fontSize: 11
                    }
                },

                visualMap: {
                    min: minValue.value,
                    max: maxValue.value,
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '5%',
                    color: colorSchemes[colorScheme.value],
                    textStyle: {
                        color: '#666'
                    }
                },

                series: [
                    {
                        name: '热力图',
                        type: 'heatmap',
                        data: props.data.flat().map((value, index) => {
                            const x = index % props.xAxis.length
                            const y = Math.floor(index / props.xAxis.length)
                            return [x, y, value]
                        }),
                        label: {
                            show: false
                        },
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        },
                        animationDelay: idx => idx * 5
                    }
                ],

                toolbox: {
                    show: !props.title,
                    feature: {
                        restore: {},
                        saveAsImage: {
                            pixelRatio: 2
                        }
                    }
                },

                animationDuration: 1000,
                animationEasing: 'cubicOut'
            }

            // 设置配置并渲染
            chartInstance.setOption(option, true)

            // 绑定事件
            bindEvents()

            // 通知父组件
            emit('ready', chartInstance)
        } catch (err) {
            error.value = err.message || '热力图初始化失败'
            emit('error', err)
            console.error('AdvancedHeatmap initialization error:', err)
        } finally {
            loading.value = false
        }
    }

    // 绑定事件
    const bindEvents = () => {
        if (!chartInstance) return

        // 单元格点击事件
        chartInstance.on('click', params => {
            if (params.seriesType === 'heatmap') {
                const xIndex = params.data[0]
                const yIndex = params.data[1]
                const value = params.data[2]

                emit('cell-click', {
                    xIndex,
                    yIndex,
                    xLabel: props.xAxis[xIndex],
                    yLabel: props.yAxis[yIndex],
                    value,
                    event: params
                })
            }
        })

        // 鼠标离开隐藏tooltip
        chartInstance.on('mouseout', () => {
            tooltipVisible.value = false
        })
    }

    // 更新颜色方案
    const updateColorScheme = () => {
        initChart()
    }

    // 切换视图模式
    const toggleViewMode = () => {
        showTooltip.value = !showTooltip.value
    }

    // 重置缩放
    const resetZoom = () => {
        if (chartInstance) {
            chartInstance.dispatchAction({
                type: 'restore'
            })
        }
    }

    // 导出图表
    const exportChart = async () => {
        if (!chartInstance) return

        try {
            exporting.value = true

            const dataURL = chartInstance.getDataURL({
                pixelRatio: 2,
                backgroundColor: '#fff'
            })

            // 创建下载链接
            const link = document.createElement('a')
            link.download = `${props.title || 'heatmap'}.png`
            link.href = dataURL
            link.click()
        } catch (err) {
            console.error('Export error:', err)
        } finally {
            exporting.value = false
        }
    }

    // 重试
    const retry = () => {
        initChart()
    }

    // 格式化数字
    const formatNumber = value => {
        if (typeof value !== 'number') return value
        return props.valueFormatter(value)
    }

    // 响应式调整
    const resize = () => {
        if (chartInstance) {
            chartInstance.resize()
        }
    }

    // 监听数据变化
    watch(
        [() => props.data, () => props.xAxis, () => props.yAxis],
        () => {
            nextTick(() => initChart())
        },
        { deep: true }
    )

    watch(
        () => props.colorScheme,
        newScheme => {
            colorScheme.value = newScheme
            initChart()
        }
    )

    // 生命周期
    onMounted(() => {
        initChart()
        window.addEventListener('resize', resize)
    })

    onUnmounted(() => {
        window.removeEventListener('resize', resize)
        if (chartInstance) {
            chartInstance.dispose()
            chartInstance = null
        }
    })

    // 暴露方法
    defineExpose({
        chartInstance,
        initChart,
        updateColorScheme,
        resetZoom,
        exportChart,
        resize
    })
</script>

<style scoped lang="scss">
    .advanced-heatmap-container {
        position: relative;
        width: 100%;
        height: 100%;

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e0e0e0;
            flex-wrap: wrap;
            gap: 12px;

            .chart-title {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #333;
            }

            .chart-toolbar {
                display: flex;
                gap: 8px;
                align-items: center;
            }
        }

        .chart-stats {
            display: flex;
            gap: 24px;
            margin-bottom: 16px;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            flex-wrap: wrap;

            .stat-item {
                display: flex;
                align-items: center;
                gap: 8px;

                .stat-label {
                    font-size: 14px;
                    color: #666;
                    font-weight: 500;
                }

                .stat-value {
                    font-size: 14px;
                    color: #333;
                    font-weight: 600;
                    font-family: 'Monaco', 'Menlo', monospace;
                }
            }
        }

        .chart-loading,
        .chart-error {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;

            .el-icon {
                font-size: 24px;
                margin-bottom: 8px;
            }
        }

        .chart-loading {
            color: #666;

            span {
                display: block;
                font-size: 14px;
            }
        }

        .chart-error {
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

            .el-alert {
                margin-bottom: 12px;
            }
        }

        .chart-tooltip {
            position: fixed;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 14px;
            pointer-events: none;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            max-width: 200px;

            .tooltip-header {
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 13px;
            }

            .tooltip-value {
                font-size: 16px;
                font-weight: 700;
                color: #4fc3f7;
                margin-bottom: 4px;
            }

            .tooltip-percentage {
                font-size: 12px;
                color: #81c784;
                font-weight: 500;
            }
        }
    }

    // 响应式设计
    @media (max-width: 768px) {
        .advanced-heatmap-container {
            .chart-header {
                flex-direction: column;
                align-items: flex-start;

                .chart-title {
                    font-size: 16px;
                }

                .chart-toolbar {
                    width: 100%;

                    .el-select {
                        flex: 1;
                    }
                }
            }

            .chart-stats {
                .stat-item {
                    font-size: 12px;
                }
            }
        }
    }
</style>
