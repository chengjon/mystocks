<template>
    <div class="tree-chart-container">
        <div class="chart-header" v-if="title">
            <h3 class="chart-title">{{ title }}</h3>
            <div class="chart-toolbar">
                <el-select v-model="layoutType" size="small" @change="updateLayout" style="width: 120px">
                    <el-option label="自顶向下" value="TB" />
                    <el-option label="自左向右" value="LR" />
                    <el-option label="自右向左" value="RL" />
                    <el-option label="自底向上" value="BT" />
                </el-select>
                <el-button size="small" @click="toggleLabels">
                    <el-icon><View /></el-icon>
                    {{ showLabels ? '隐藏标签' : '显示标签' }}
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
            <span>构建树状结构...</span>
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
    import { View, Refresh, Loading } from '@element-plus/icons-vue'

    const props = defineProps({
        data: {
            type: Object,
            default: () => ({ name: 'Root', children: [] })
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
            default: 'TB', // TB, LR, RL, BT
            validator: value => ['TB', 'LR', 'RL', 'BT'].includes(value)
        },
        symbolSize: {
            type: [Number, Function],
            default: val => Math.max(val * 2, 10)
        },
        roam: {
            type: [Boolean, String],
            default: true
        },
        scaleLimit: {
            type: Object,
            default: () => ({ min: 0.5, max: 2 })
        },
        emphasis: {
            type: Object,
            default: () => ({ focus: 'descendant' })
        }
    })

    const emit = defineEmits(['node-click', 'ready', 'error'])

    const chartRef = ref()
    let chartInstance = null
    const loading = ref(false)
    const error = ref('')
    const layoutType = ref(props.layout)
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
            const processedData = processTreeData(props.data)

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
                        const data = params.data
                        let content = `<strong>${data.name}</strong>`
                        if (data.value !== undefined) {
                            content += `<br/>值: ${data.value}`
                        }
                        if (data.description) {
                            content += `<br/>描述: ${data.description}`
                        }
                        return content
                    }
                },

                series: [
                    {
                        type: 'tree',
                        data: [processedData],
                        layout: layoutType.value,
                        orient: getOrientFromLayout(layoutType.value),

                        symbolSize: props.symbolSize,
                        roam: props.roam,
                        scaleLimit: props.scaleLimit,
                        emphasis: props.emphasis,

                        label: {
                            show: showLabels.value,
                            position: getLabelPosition(layoutType.value),
                            fontSize: 12,
                            color: '#333',
                            formatter: '{b}'
                        },

                        leaves: {
                            label: {
                                show: showLabels.value,
                                position: getLeafLabelPosition(layoutType.value),
                                fontSize: 11,
                                color: '#666'
                            }
                        },

                        itemStyle: {
                            borderWidth: 2,
                            borderColor: '#fff',
                            shadowBlur: 4,
                            shadowColor: 'rgba(0, 0, 0, 0.1)'
                        },

                        lineStyle: {
                            color: FINANCIAL_COLORS.grid,
                            width: 2,
                            curveness: 0.2
                        },

                        animationDuration: 1000,
                        animationEasing: 'cubicOut'
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
                }
            }

            // 设置配置并渲染
            chartInstance.setOption(option, true)

            // 绑定事件
            bindEvents()

            // 通知父组件
            emit('ready', chartInstance)
        } catch (err) {
            error.value = err.message || '树状图初始化失败'
            emit('error', err)
            console.error('TreeChart initialization error:', err)
        } finally {
            loading.value = false
        }
    }

    // 处理树状数据
    const processTreeData = (node, level = 0) => {
        const colors = [
            FINANCIAL_COLORS.primary,
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
        ]

        return {
            name: node.name,
            value: node.value || node.children?.length || 1,
            description: node.description,

            itemStyle: {
                color: node.color || colors[level % colors.length]
            },

            label: {
                show: showLabels.value && (level < 3 || node.showLabel), // 只显示前3层标签
                fontSize: Math.max(16 - level * 2, 10) // 层级越深字体越小
            },

            children: node.children?.map(child => processTreeData(child, level + 1)),

            // 保留原始属性
            ...node
        }
    }

    // 根据布局获取方向
    const getOrientFromLayout = layout => {
        switch (layout) {
            case 'TB':
                return 'TB'
            case 'BT':
                return 'BT'
            case 'LR':
                return 'LR'
            case 'RL':
                return 'RL'
            default:
                return 'TB'
        }
    }

    // 根据布局获取标签位置
    const getLabelPosition = layout => {
        switch (layout) {
            case 'TB':
                return 'bottom'
            case 'BT':
                return 'top'
            case 'LR':
                return 'right'
            case 'RL':
                return 'left'
            default:
                return 'bottom'
        }
    }

    // 获取叶子节点标签位置
    const getLeafLabelPosition = layout => {
        switch (layout) {
            case 'TB':
                return 'top'
            case 'BT':
                return 'bottom'
            case 'LR':
                return 'left'
            case 'RL':
                return 'right'
            default:
                return 'top'
        }
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
            }
        })
    }

    // 更新布局
    const updateLayout = () => {
        initChart()
    }

    // 切换标签显示
    const toggleLabels = () => {
        showLabels.value = !showLabels.value
        initChart()
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

    watch(layoutType, () => {
        initChart()
    })

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
        resetZoom,
        resize,
        toggleLabels
    })
</script>

<style scoped lang="scss">
    .tree-chart-container {
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
        .tree-chart-container {
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

                    .el-button {
                        flex: 1;
                    }
                }
            }
        }
    }
</style>
