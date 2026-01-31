<template>
    <div class="relation-chart-container">
        <div class="chart-header" v-if="title">
            <h3 class="chart-title">{{ title }}</h3>
            <div class="chart-toolbar">
                <el-button size="small" @click="toggleLabels">
                    <el-icon><View /></el-icon>
                    {{ showLabels ? '隐藏标签' : '显示标签' }}
                </el-button>
                <el-button size="small" @click="resetLayout">
                    <el-icon><Refresh /></el-icon>
                    重置布局
                </el-button>
                <el-button size="small" @click="exportChart" :loading="exporting">
                    <el-icon><Download /></el-icon>
                    导出
                </el-button>
            </div>
        </div>

        <div class="chart-legend" v-if="categories.length > 0">
            <div class="legend-item" v-for="category in categories" :key="category.name">
                <div class="legend-color" :style="{ backgroundColor: category.itemStyle?.color || '#5470c6' }"></div>
                <span class="legend-text">{{ category.name }}</span>
            </div>
        </div>

        <div ref="chartRef" :style="{ width: width, height: height }"></div>

        <div class="chart-loading" v-if="loading">
            <el-icon class="is-loading">
                <Loading />
            </el-icon>
            <span>分析关系网络...</span>
        </div>

        <div class="chart-error" v-if="error">
            <el-alert :title="error" type="error" :closable="false" show-icon />
            <el-button @click="retry" size="small">重试</el-button>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
    import * as echarts from 'echarts'
    import { getAdaptiveTheme, FINANCIAL_COLORS } from '@/styles/chart-theme'
    import { View, Refresh, Download, Loading } from '@element-plus/icons-vue'

    const props = defineProps({
        nodes: {
            type: Array,
            default: () => []
        },
        links: {
            type: Array,
            default: () => []
        },
        categories: {
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
        layout: {
            type: String,
            default: 'force', // force, circular, none
            validator: value => ['force', 'circular', 'none'].includes(value)
        },
        draggable: {
            type: Boolean,
            default: true
        },
        focusNodeAdjacency: {
            type: Boolean,
            default: true
        },
        roam: {
            type: [Boolean, String],
            default: true
        },
        edgeSymbol: {
            type: Array,
            default: () => ['none', 'arrow']
        },
        edgeSymbolSize: {
            type: Array,
            default: () => [10, 15]
        }
    })

    const emit = defineEmits(['node-click', 'link-click', 'ready', 'error'])

    const chartRef = ref()
    let chartInstance = null
    const loading = ref(false)
    const error = ref('')
    const exporting = ref(false)
    const showLabels = ref(true)

    // 初始化图表
    const initChart = async () => {
        if (!chartRef.value) return

        try {
            loading.value = true
            error.value = ''

            // 销毁旧实例
            if (chartInstance) {
                chartInstance.dispose()
            }

            // 创建新实例
            chartInstance = echarts.init(chartRef.value, artDecoTheme)

            // 处理数据
            const processedNodes = processNodes(props.nodes)
            const processedLinks = processLinks(props.links)
            const processedCategories = processCategories(props.categories)

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

                legend:
                    processedCategories.length > 0
                        ? {
                              data: processedCategories.map(cat => cat.name),
                              top: props.title ? 40 : 10
                          }
                        : undefined,

                tooltip: {
                    trigger: 'item',
                    formatter: params => {
                        if (params.dataType === 'node') {
                            const node = params.data
                            let content = `<strong>${node.name}</strong>`
                            if (node.value !== undefined) {
                                content += `<br/>值: ${node.value}`
                            }
                            if (node.description) {
                                content += `<br/>${node.description}`
                            }
                            return content
                        } else if (params.dataType === 'edge') {
                            const link = params.data
                            return `${link.source} → ${link.target}<br/>权重: ${link.value || 1}`
                        }
                        return params.name
                    }
                },

                series: [
                    {
                        type: 'graph',
                        layout: props.layout,
                        data: processedNodes,
                        links: processedLinks,
                        categories: processedCategories,

                        roam: props.roam,
                        draggable: props.draggable,
                        focusNodeAdjacency: props.focusNodeAdjacency,

                        label: {
                            show: showLabels.value,
                            position: 'right',
                            fontSize: 12,
                            color: '#333'
                        },

                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.3)'
                        },

                        lineStyle: {
                            color: 'source',
                            curveness: 0.3,
                            width: 2,
                            opacity: 0.8
                        },

                        emphasis: {
                            focus: 'adjacency',
                            lineStyle: {
                                width: 4
                            }
                        },

                        edgeSymbol: props.edgeSymbol,
                        edgeSymbolSize: props.edgeSymbolSize,

                        force:
                            props.layout === 'force'
                                ? {
                                      repulsion: 100,
                                      edgeLength: [50, 200],
                                      gravity: 0.2
                                  }
                                : undefined,

                        circular:
                            props.layout === 'circular'
                                ? {
                                      rotateLabel: true
                                  }
                                : undefined
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

                animationDuration: 1500,
                animationEasingUpdate: 'quinticInOut'
            }

            // 设置配置并渲染
            chartInstance.setOption(option, true)

            // 绑定事件
            bindEvents()

            // 通知父组件
            emit('ready', chartInstance)
        } catch (err) {
            error.value = err.message || '关系图初始化失败'
            emit('error', err)
            console.error('RelationChart initialization error:', err)
        } finally {
            loading.value = false
        }
    }

    // 处理节点数据
    const processNodes = nodes => {
        const defaultColors = [
            FINANCIAL_COLORS.primary,
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
        ]

        return nodes.map((node, index) => ({
            id: node.id || node.name,
            name: node.name,
            value: node.value || 1,
            symbolSize: node.symbolSize || Math.max(Math.min(node.value || 20, 60), 10),
            category: node.category || 0,

            itemStyle: {
                color: node.itemStyle?.color || defaultColors[index % defaultColors.length]
            },

            label: {
                show: showLabels.value && node.symbolSize > 20, // 小节点不显示标签
                fontSize: Math.max(12 - Math.floor(node.symbolSize / 10), 8)
            },

            // 保留其他属性
            ...node
        }))
    }

    // 处理连线数据
    const processLinks = links => {
        return links.map(link => ({
            source: link.source,
            target: link.target,
            value: link.value || 1,

            lineStyle: {
                color: link.lineStyle?.color || FINANCIAL_COLORS.grid,
                width: link.lineStyle?.width || 2,
                opacity: link.lineStyle?.opacity || 0.8,
                curveness: link.lineStyle?.curveness || 0.3
            },

            // 保留其他属性
            ...link
        }))
    }

    // 处理分类数据
    const processCategories = categories => {
        const defaultColors = [
            FINANCIAL_COLORS.primary,
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
        ]

        return categories.map((category, index) => ({
            name: category.name,
            itemStyle: {
                color: category.itemStyle?.color || defaultColors[index % defaultColors.length]
            },
            ...category
        }))
    }

    // 绑定事件
    const bindEvents = () => {
        if (!chartInstance) return

        // 节点点击事件
        chartInstance.on('click', params => {
            if (params.dataType === 'node') {
                emit('node-click', {
                    node: params.data,
                    event: params
                })
            } else if (params.dataType === 'edge') {
                emit('link-click', {
                    link: params.data,
                    event: params
                })
            }
        })
    }

    // 切换标签显示
    const toggleLabels = () => {
        showLabels.value = !showLabels.value
        initChart()
    }

    // 重置布局
    const resetLayout = () => {
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
            link.download = `${props.title || 'relation-chart'}.png`
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

    // 响应式调整
    const resize = () => {
        if (chartInstance) {
            chartInstance.resize()
        }
    }

    // 监听数据变化
    watch(
        [() => props.nodes, () => props.links, () => props.categories],
        () => {
            nextTick(() => initChart())
        },
        { deep: true }
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
        toggleLabels,
        resetLayout,
        exportChart,
        resize
    })
</script>

<style scoped lang="scss">
    .relation-chart-container {
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
            }
        }

        .chart-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 16px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            border: 1px solid #e0e0e0;

            .legend-item {
                display: flex;
                align-items: center;
                gap: 8px;

                .legend-color {
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    border: 2px solid #fff;
                    box-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
                }

                .legend-text {
                    font-size: 14px;
                    color: #666;
                    font-weight: 500;
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
    }

    // 响应式设计
    @media (max-width: 768px) {
        .relation-chart-container {
            .chart-header {
                flex-direction: column;
                align-items: flex-start;

                .chart-title {
                    font-size: 16px;
                }

                .chart-toolbar {
                    width: 100%;
                    justify-content: flex-end;
                    flex-wrap: wrap;
                }
            }

            .chart-legend {
                .legend-item {
                    font-size: 12px;
                }
            }
        }
    }
</style>
