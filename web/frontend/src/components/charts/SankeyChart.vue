<template>
    <div class="sankey-chart-container">
        <div class="chart-header" v-if="title">
            <h3 class="chart-title">{{ title }}</h3>
            <div class="chart-toolbar">
                <el-button size="small" @click="exportChart" :loading="exporting">
                    <el-icon><Download /></el-icon>
                    导出
                </el-button>
                <el-button size="small" @click="resetZoom">
                    <el-icon><Refresh /></el-icon>
                    重置
                </el-button>
            </div>
        </div>

        <div ref="chartRef" :style="{ width: width, height: height }"></div>

        <div class="chart-loading" v-if="loading">
            <el-icon class="is-loading">
                <Loading />
            </el-icon>
            <span>加载中...</span>
        </div>

        <div class="chart-error" v-if="error">
            <el-alert :title="error" type="error" :closable="false" show-icon />
            <el-button @click="retry" size="small">重试</el-button>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
    import echarts from '@/utils/echarts'
    import { artDecoTheme } from '@/utils/echarts'
    import { Download, Refresh, Loading } from '@element-plus/icons-vue'

    const props = defineProps({
        data: {
            type: Object,
            default: () => ({ nodes: [], links: [] })
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
        orient: {
            type: String,
            default: 'horizontal', // horizontal or vertical
            validator: value => ['horizontal', 'vertical'].includes(value)
        },
        nodeWidth: {
            type: Number,
            default: 20
        },
        nodeGap: {
            type: Number,
            default: 8
        },
        draggable: {
            type: Boolean,
            default: true
        },
        focusNodeAdjacency: {
            type: Boolean,
            default: true
        },
        levels: {
            type: Array,
            default: () => []
        }
    })

    const emit = defineEmits(['node-click', 'link-click', 'ready', 'error'])

    const chartRef = ref()
    let chartInstance = null
    const loading = ref(false)
    const error = ref('')
    const exporting = ref(false)

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

            // 准备数据
            const { nodes, links } = props.data
            const processedNodes = processNodes(nodes)
            const processedLinks = processLinks(links)

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
                    triggerOn: 'mousemove',
                    formatter: params => {
                        if (params.dataType === 'node') {
                            return `${params.data.name}: ${params.data.value || 0}`
                        } else if (params.dataType === 'edge') {
                            return `${params.data.source} → ${params.data.target}: ${params.data.value || 0}`
                        }
                        return params.name
                    }
                },

                series: [
                    {
                        type: 'sankey',
                        data: processedNodes,
                        links: processedLinks,
                        orient: props.orient,
                        nodeWidth: props.nodeWidth,
                        nodeGap: props.nodeGap,
                        draggable: props.draggable,
                        focusNodeAdjacency: props.focusNodeAdjacency,
                        levels: props.levels.length > 0 ? props.levels : undefined,

                        itemStyle: {
                            borderWidth: 1,
                            borderColor: '#fff'
                        },

                        lineStyle: {
                            color: 'source',
                            curveness: 0.3
                        },

                        emphasis: {
                            focus: 'adjacency'
                        },

                        label: {
                            fontSize: 12,
                            color: '#333'
                        },

                        tooltip: {
                            trigger: 'item'
                        }
                    }
                ],

                toolbox: {
                    show: !props.title, // 如果有自定义标题栏，隐藏工具箱
                    feature: {
                        restore: {},
                        saveAsImage: {
                            pixelRatio: 2
                        }
                    }
                }
            }

            // 设置配置并渲染
            chartInstance.setOption(option, true)

            // 绑定事件
            bindEvents()

            // 通知父组件
            emit('ready', chartInstance)
        } catch (err) {
            error.value = err.message || '图表初始化失败'
            emit('error', err)
            console.error('SankeyChart initialization error:', err)
        } finally {
            loading.value = false
        }
    }

    // 处理节点数据
    const processNodes = nodes => {
        return nodes.map(node => ({
            name: node.name,
            value: node.value || 0,
            itemStyle: {
                color: node.color || undefined
            },
            label: {
                show: node.showLabel !== false,
                position: node.labelPosition || 'right',
                fontSize: node.fontSize || 12
            },
            ...node // 保留其他属性
        }))
    }

    // 处理连线数据
    const processLinks = links => {
        return links.map(link => ({
            source: link.source,
            target: link.target,
            value: link.value || 0,
            lineStyle: {
                color: link.color || 'source',
                width: link.width || undefined,
                opacity: link.opacity || 0.8
            },
            ...link // 保留其他属性
        }))
    }

    // 绑定事件
    const bindEvents = () => {
        if (!chartInstance) return

        // 节点点击事件
        chartInstance.on('click', 'series.sankey.data', params => {
            emit('node-click', {
                node: params.data,
                event: params
            })
        })

        // 连线点击事件
        chartInstance.on('click', 'series.sankey.links', params => {
            emit('link-click', {
                link: params.data,
                event: params
            })
        })
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
            link.download = `${props.title || 'sankey-chart'}.png`
            link.href = dataURL
            link.click()
        } catch (err) {
            console.error('Export error:', err)
        } finally {
            exporting.value = false
        }
    }

    // 重置缩放
    const resetZoom = () => {
        if (chartInstance) {
            chartInstance.dispatchAction({
                type: 'restore'
            })
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
        () => props.data,
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
        exportChart,
        resetZoom,
        resize
    })
</script>

<style scoped lang="scss">
    @use '@/styles/artdeco-tokens.scss' as *;

    .sankey-chart-container {
        position: relative;
        width: 100%;
        height: 100%;

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);
            padding-bottom: var(--artdeco-spacing-3);
            border-bottom: 1px solid var(--artdeco-border-default);

            .chart-title {
                margin: 0;
                font-family: var(--artdeco-font-heading, var(--font-display));
                font-size: var(--artdeco-text-lg);
                font-weight: var(--artdeco-font-semibold);
                color: var(--artdeco-gold-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }

            .chart-toolbar {
                display: flex;
                gap: var(--artdeco-spacing-2);
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
                font-size: var(--artdeco-spacing-6);
                margin-bottom: var(--artdeco-spacing-2);
            }
        }

        .chart-loading {
            color: var(--artdeco-fg-muted);

            span {
                display: block;
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }

        .chart-error {
            background: color-mix(in srgb, var(--artdeco-bg-global) 92%, var(--artdeco-bg-card));
            padding: var(--artdeco-spacing-5);
            border: 1px solid var(--artdeco-border-default);
            border-radius: var(--artdeco-radius-none);
            box-shadow: var(--artdeco-shadow-lg), var(--artdeco-glow-subtle);

            .el-alert {
                margin-bottom: var(--artdeco-spacing-3);
            }
        }
    }

    @media (width <= 48rem) {
        .sankey-chart-container {
            .chart-header {
                flex-direction: column;
                gap: var(--artdeco-spacing-3);
                align-items: flex-start;

                .chart-title {
                    font-size: var(--artdeco-text-base);
                }

                .chart-toolbar {
                    width: 100%;
                    justify-content: flex-end;
                }
            }
        }
    }
</style>
