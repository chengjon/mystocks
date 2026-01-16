<!-- DataVisualizationShowcase.vue - 数据可视化增强功能展示 -->
<template>
    <div class="data-viz-showcase">
        <div class="showcase-header">
            <h1>数据可视化增强展示</h1>
            <p>展示统一图表主题和高级图表组件功能</p>
        </div>

        <div class="theme-selector">
            <h3>图表主题选择</h3>
            <el-radio-group v-model="currentTheme" @change="updateTheme">
                <el-radio-button label="default">默认主题</el-radio-button>
                <el-radio-button label="dark">暗色主题</el-radio-button>
                <el-radio-button label="compact">紧凑主题</el-radio-button>
                <el-radio-button label="mobile">移动端主题</el-radio-button>
            </el-radio-group>
        </div>

        <!-- 桑基图示例 -->
        <el-card class="chart-section" shadow="hover">
            <template #header>
                <div class="section-header">
                    <h3>资金流向桑基图</h3>
                    <p>展示资金在不同板块间的流动关系</p>
                </div>
            </template>

            <SankeyChart
                :data="sankeyData"
                title="A股资金流向分析"
                height="400px"
                @ready="onChartReady('sankey', $event)"
                @node-click="onNodeClick"
                @link-click="onLinkClick"
            />
        </el-card>

        <!-- 树状图示例 -->
        <el-card class="chart-section" shadow="hover">
            <template #header>
                <div class="section-header">
                    <h3>行业板块树状图</h3>
                    <p>展示行业板块的层级结构关系</p>
                </div>
            </template>

            <TreeChart
                :data="treeData"
                title="A股行业板块结构"
                height="400px"
                @ready="onChartReady('tree', $event)"
                @node-click="onNodeClick"
            />
        </el-card>

        <!-- 关系图示例 -->
        <el-card class="chart-section" shadow="hover">
            <template #header>
                <div class="section-header">
                    <h3>股票关联关系图</h3>
                    <p>展示股票之间的关联关系网络</p>
                </div>
            </template>

            <RelationChart
                :nodes="relationNodes"
                :links="relationLinks"
                :categories="relationCategories"
                title="热门股票关联分析"
                height="400px"
                @ready="onChartReady('relation', $event)"
                @node-click="onNodeClick"
                @link-click="onLinkClick"
            />
        </el-card>

        <!-- 增强热力图示例 -->
        <el-card class="chart-section" shadow="hover">
            <template #header>
                <div class="section-header">
                    <h3>市场情绪热力图</h3>
                    <p>展示不同板块的市场情绪强度分布</p>
                </div>
            </template>

            <AdvancedHeatmap
                :data="heatmapData"
                :x-axis="heatmapXAxis"
                :y-axis="heatmapYAxis"
                title="板块情绪热力图"
                height="400px"
                :color-scheme="colorScheme"
                @ready="onChartReady('heatmap', $event)"
                @cell-click="onCellClick"
            />
        </el-card>

        <!-- 传统图表对比 -->
        <el-card class="chart-section" shadow="hover">
            <template #header>
                <div class="section-header">
                    <h3>传统图表 (ECharts标准组件)</h3>
                    <p>对比展示传统K线图和标准热力图</p>
                </div>
            </template>

            <div class="traditional-charts">
                <div class="chart-item">
                    <h4>K线图示例</h4>
                    <div ref="klineChartRef" style="height: 300px"></div>
                </div>
                <div class="chart-item">
                    <h4>标准热力图</h4>
                    <div ref="standardHeatmapRef" style="height: 300px"></div>
                </div>
            </div>
        </el-card>

        <!-- 功能特性展示 -->
        <el-card class="features-section" shadow="hover">
            <template #header>
                <h3>可视化增强特性</h3>
            </template>

            <div class="features-grid">
                <div class="feature-item">
                    <el-icon class="feature-icon"><Palette /></el-icon>
                    <h4>统一主题系统</h4>
                    <p>金融主题色彩、响应式设计、暗色模式支持</p>
                </div>

                <div class="feature-item">
                    <el-icon class="feature-icon"><DataAnalysis /></el-icon>
                    <h4>高级图表类型</h4>
                    <p>桑基图、树状图、关系图、增强热力图等专业图表</p>
                </div>

                <div class="feature-item">
                    <el-icon class="feature-icon"><Setting /></el-icon>
                    <h4>智能交互</h4>
                    <p>拖拽、缩放、联动、数据筛选等交互功能</p>
                </div>

                <div class="feature-item">
                    <el-icon class="feature-icon"><Download /></el-icon>
                    <h4>导出功能</h4>
                    <p>支持PNG、SVG等多种格式的图表导出</p>
                </div>

                <div class="feature-item">
                    <el-icon class="feature-icon"><Monitor /></el-icon>
                    <h4>性能优化</h4>
                    <p>大数据渲染优化、内存管理、懒加载支持</p>
                </div>

                <div class="feature-item">
                    <el-icon class="feature-icon"><Mobile /></el-icon>
                    <h4>移动端适配</h4>
                    <p>触摸优化、响应式布局、自适应主题</p>
                </div>
            </div>
        </el-card>

        <!-- 事件日志 -->
        <el-card class="logs-section" shadow="hover">
            <template #header>
                <h3>交互事件日志</h3>
            </template>

            <div class="event-logs">
                <div v-for="(log, index) in eventLogs.slice(-10)" :key="index" class="log-item">
                    <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                    <span class="log-type" :class="log.type">{{ log.type }}</span>
                    <span class="log-message">{{ log.message }}</span>
                </div>
                <div v-if="eventLogs.length === 0" class="no-logs">点击图表元素查看交互日志</div>
            </div>

            <div class="log-actions">
                <el-button size="small" @click="clearLogs">清空日志</el-button>
                <el-button size="small" @click="exportLogs">导出日志</el-button>
            </div>
        </el-card>
    </div>
</template>

<script setup>
    import { ref, onMounted, onUnmounted } from 'vue'
    import * as echarts from 'echarts'
    import { getChartTheme } from '@/styles/chart-theme'

    // 导入新创建的高级图表组件
    import SankeyChart from '@/components/charts/SankeyChart.vue'
    import TreeChart from '@/components/charts/TreeChart.vue'
    import RelationChart from '@/components/charts/RelationChart.vue'
    import AdvancedHeatmap from '@/components/charts/AdvancedHeatmap.vue'

    // 图标
    import { Palette, DataAnalysis, Setting, Download, Monitor, Mobile } from '@element-plus/icons-vue'

    // 响应式数据
    const currentTheme = ref('default')
    const colorScheme = ref('financial')
    const eventLogs = ref([])
    const klineChartRef = ref()
    const standardHeatmapRef = ref()
    let klineChart = null
    let standardHeatmap = null

    // 模拟数据生成
    const generateMockData = () => {
        // 桑基图数据 - 资金流向
        const sankeyData = {
            nodes: [
                { name: '北向资金' },
                { name: '主力资金' },
                { name: '散户资金' },
                { name: '沪深300' },
                { name: '创业板' },
                { name: '科创板' },
                { name: '资金流出' }
            ],
            links: [
                { source: '北向资金', target: '沪深300', value: 120 },
                { source: '北向资金', target: '创业板', value: 80 },
                { source: '主力资金', target: '沪深300', value: 200 },
                { source: '主力资金', target: '创业板', value: 150 },
                { source: '主力资金', target: '科创板', value: 100 },
                { source: '散户资金', target: '沪深300', value: 50 },
                { source: '散户资金', target: '创业板', value: 30 },
                { source: '沪深300', target: '资金流出', value: 80 },
                { source: '创业板', target: '资金流出', value: 60 },
                { source: '科创板', target: '资金流出', value: 40 }
            ]
        }

        // 树状图数据 - 行业板块
        const treeData = {
            name: 'A股市场',
            children: [
                {
                    name: '上证指数',
                    children: [
                        { name: '金融板块', value: 30 },
                        { name: '地产板块', value: 25 },
                        { name: '基建板块', value: 20 },
                        { name: '消费板块', value: 15 }
                    ]
                },
                {
                    name: '深证指数',
                    children: [
                        { name: '新能源', value: 35 },
                        { name: '半导体', value: 30 },
                        { name: '医药板块', value: 25 },
                        { name: '化工板块', value: 20 }
                    ]
                },
                {
                    name: '创业板',
                    children: [
                        { name: 'TMT板块', value: 40 },
                        { name: '生物医药', value: 35 },
                        { name: '新能源汽车', value: 30 }
                    ]
                }
            ]
        }

        // 关系图数据 - 股票关联
        const relationNodes = [
            { id: '000001', name: '平安银行', symbolSize: 40, category: 0 },
            { id: '000002', name: '万科A', symbolSize: 35, category: 1 },
            { id: '600036', name: '招商银行', symbolSize: 38, category: 0 },
            { id: '600519', name: '贵州茅台', symbolSize: 42, category: 2 },
            { id: '000858', name: '五粮液', symbolSize: 32, category: 2 },
            { id: '300750', name: '宁德时代', symbolSize: 36, category: 3 }
        ]

        const relationLinks = [
            { source: '000001', target: '000002', value: 8 },
            { source: '000001', target: '600036', value: 10 },
            { source: '600036', target: '000002', value: 6 },
            { source: '600519', target: '000858', value: 12 },
            { source: '300750', target: '600519', value: 9 }
        ]

        const relationCategories = [
            { name: '银行股', itemStyle: { color: '#5470c6' } },
            { name: '地产股', itemStyle: { color: '#91cc75' } },
            { name: '白酒股', itemStyle: { color: '#fac858' } },
            { name: '新能源', itemStyle: { color: '#ee6666' } }
        ]

        // 热力图数据 - 市场情绪
        const heatmapData = Array.from({ length: 8 }, () => Array.from({ length: 12 }, () => Math.random() * 100))
        const heatmapXAxis = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        const heatmapYAxis = [
            '上证指数',
            '深证成指',
            '创业板指',
            '沪深300',
            '中证500',
            '中证1000',
            '科创50',
            '创业板ETF'
        ]

        return {
            sankeyData,
            treeData,
            relationNodes,
            relationLinks,
            relationCategories,
            heatmapData,
            heatmapXAxis,
            heatmapYAxis
        }
    }

    const mockData = generateMockData()

    // 解构数据
    const {
        sankeyData,
        treeData,
        relationNodes,
        relationLinks,
        relationCategories,
        heatmapData,
        heatmapXAxis,
        heatmapYAxis
    } = mockData

    // 事件处理
    const onChartReady = (chartType, instance) => {
        addLog('success', `${chartType}图表初始化完成`)
        console.log(`${chartType} chart ready:`, instance)
    }

    const onNodeClick = data => {
        addLog('info', `点击节点: ${data.node?.name || data.node?.id}`)
    }

    const onLinkClick = data => {
        addLog('info', `点击连线: ${data.link?.source} → ${data.link?.target}`)
    }

    const onCellClick = data => {
        addLog('info', `点击热力图单元格: ${data.xLabel}×${data.yLabel} = ${data.value}`)
    }

    // 主题切换
    const updateTheme = () => {
        // 这里可以全局更新所有图表的主题
        addLog('info', `切换到${currentTheme.value}主题`)
    }

    // 日志管理
    const addLog = (type, message) => {
        eventLogs.value.push({
            type,
            message,
            timestamp: Date.now()
        })
    }

    const clearLogs = () => {
        eventLogs.value = []
    }

    const exportLogs = () => {
        const dataStr = JSON.stringify(eventLogs.value, null, 2)
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)

        const exportFileDefaultName = 'chart-interaction-logs.json'

        const linkElement = document.createElement('a')
        linkElement.setAttribute('href', dataUri)
        linkElement.setAttribute('download', exportFileDefaultName)
        linkElement.click()
    }

    const formatTime = timestamp => {
        return new Date(timestamp).toLocaleTimeString()
    }

    // 初始化传统图表
    const initTraditionalCharts = () => {
        // K线图
        if (klineChartRef.value) {
            klineChart = echarts.init(klineChartRef.value, getChartTheme(currentTheme.value))
            const klineOption = {
                title: { text: '上证指数K线图', left: 'center' },
                xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
                yAxis: { type: 'value' },
                series: [
                    {
                        type: 'candlestick',
                        data: [
                            [20, 34, 10, 38],
                            [34, 50, 25, 42],
                            [50, 40, 35, 55],
                            [40, 45, 30, 50],
                            [45, 60, 40, 55],
                            [60, 55, 45, 65]
                        ]
                    }
                ]
            }
            klineChart.setOption(klineOption)
        }

        // 标准热力图
        if (standardHeatmapRef.value) {
            standardHeatmap = echarts.init(standardHeatmapRef.value, getChartTheme(currentTheme.value))
            const heatmapOption = {
                title: { text: '标准热力图', left: 'center' },
                xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
                yAxis: { type: 'category', data: ['1', '2', '3', '4'] },
                visualMap: { min: 0, max: 100, calculable: true },
                series: [
                    {
                        type: 'heatmap',
                        data: [
                            [0, 0, 10],
                            [1, 0, 20],
                            [2, 0, 30],
                            [3, 0, 40],
                            [4, 0, 50],
                            [0, 1, 15],
                            [1, 1, 25],
                            [2, 1, 35],
                            [3, 1, 45],
                            [4, 1, 55],
                            [0, 2, 20],
                            [1, 2, 30],
                            [2, 2, 40],
                            [3, 2, 50],
                            [4, 2, 60],
                            [0, 3, 25],
                            [1, 3, 35],
                            [2, 3, 45],
                            [3, 3, 55],
                            [4, 3, 65]
                        ]
                    }
                ]
            }
            standardHeatmap.setOption(heatmapOption)
        }
    }

    // 监听主题变化
    watch(currentTheme, () => {
        // 重新初始化传统图表以应用新主题
        if (klineChart) klineChart.dispose()
        if (standardHeatmap) standardHeatmap.dispose()
        nextTick(() => initTraditionalCharts())
    })

    // 生命周期
    onMounted(() => {
        initTraditionalCharts()
    })

    onUnmounted(() => {
        if (klineChart) klineChart.dispose()
        if (standardHeatmap) standardHeatmap.dispose()
    })
</script>

<style scoped lang="scss">
    .data-viz-showcase {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .showcase-header {
        text-align: center;
        margin-bottom: 40px;

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5rem;
            font-weight: 300;
        }

        p {
            color: #7f8c8d;
            font-size: 1.1rem;
        }
    }

    .theme-selector {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 30px;
        border: 1px solid #e9ecef;

        h3 {
            margin: 0 0 15px 0;
            color: #495057;
            font-size: 1.2rem;
        }

        .el-radio-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
    }

    .chart-section {
        margin-bottom: 30px;

        .section-header {
            h3 {
                margin: 0 0 8px 0;
                color: #495057;
                font-size: 1.4rem;
            }

            p {
                margin: 0;
                color: #6c757d;
                font-size: 0.9rem;
            }
        }
    }

    .traditional-charts {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 20px;

        .chart-item {
            h4 {
                margin: 0 0 15px 0;
                color: #495057;
                font-size: 1.1rem;
                text-align: center;
            }
        }
    }

    .features-section {
        margin-bottom: 30px;

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;

            .feature-item {
                text-align: center;
                padding: 20px;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background: #f8f9fa;

                .feature-icon {
                    font-size: 32px;
                    color: #007bff;
                    margin-bottom: 15px;
                }

                h4 {
                    margin: 0 0 10px 0;
                    color: #495057;
                    font-size: 1.1rem;
                }

                p {
                    margin: 0;
                    color: #6c757d;
                    font-size: 0.9rem;
                    line-height: 1.5;
                }
            }
        }
    }

    .logs-section {
        .event-logs {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            margin-bottom: 15px;

            .log-item {
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 8px 12px;
                border-bottom: 1px solid #f8f9fa;

                &:last-child {
                    border-bottom: none;
                }

                .log-time {
                    color: #6c757d;
                    font-size: 0.8rem;
                    font-family: monospace;
                    min-width: 80px;
                }

                .log-type {
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    text-transform: uppercase;

                    &.success {
                        background: #d4edda;
                        color: #155724;
                    }

                    &.info {
                        background: #cce5ff;
                        color: #004085;
                    }

                    &.warning {
                        background: #fff3cd;
                        color: #856404;
                    }

                    &.error {
                        background: #f8d7da;
                        color: #721c24;
                    }
                }

                .log-message {
                    flex: 1;
                    color: #495057;
                    font-size: 0.9rem;
                }
            }

            .no-logs {
                text-align: center;
                color: #6c757d;
                padding: 40px;
                font-style: italic;
            }
        }

        .log-actions {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
    }

    @media (max-width: 768px) {
        .data-viz-showcase {
            padding: 10px;
        }

        .showcase-header {
            h1 {
                font-size: 2rem;
            }
        }

        .theme-selector .el-radio-group {
            justify-content: center;
        }

        .traditional-charts {
            grid-template-columns: 1fr;
        }

        .features-grid {
            grid-template-columns: 1fr;
        }

        .logs-section .event-logs .log-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;

            .log-time {
                min-width: auto;
            }
        }
    }
</style>
