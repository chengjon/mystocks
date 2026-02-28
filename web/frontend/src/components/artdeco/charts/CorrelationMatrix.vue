<template>
    <div class="artdeco-correlation-matrix">
        <ArtDecoCard class="matrix-card">
            <template #header>
                <div class="matrix-header">
                    <div class="header-title">
                        <span class="title-icon">🎯</span>
                        <div class="title-text">
                            <div class="title-main">{{ title }}</div>
                            <div class="title-sub">{{ subtitle }}</div>
                        </div>
                    </div>
                    <div class="header-controls">
                        <ArtDecoButton @click="handleRefresh" :loading="loading" variant="secondary" size="sm">
                            ↻ 刷新
                        </ArtDecoButton>
                    </div>
                </div>
            </template>

            <div class="matrix-container" :class="{ loading: loading }">
                <ArtDecoLoader v-if="loading" :text="'加载中...'" />

                <div v-else class="matrix-content">
                    <!-- Empty State -->
                    <div v-if="!data || data.length === 0" class="empty-state">
                        <div class="empty-icon">📊</div>
                        <div class="empty-text">暂无相关性数据</div>
                        <div class="empty-hint">NO CORRELATION DATA AVAILABLE</div>
                    </div>

                    <!-- Correlation Matrix -->
                    <div v-else class="matrix-wrapper">
                        <!-- Row Headers (Left) -->
                        <div class="matrix-row-headers">
                            <div
                                v-for="(item, index) in data"
                                :key="'row-' + index"
                                class="row-header"
                                :class="{ active: selectedRow === index }"
                                @click="handleRowClick(index)"
                                @mouseenter="handleRowHover(index)"
                                @mouseleave="handleRowLeave"
                            >
                                {{ item.symbol }}
                            </div>
                        </div>

                        <!-- Matrix Grid -->
                        <div class="matrix-grid">
                            <!-- Column Headers (Top) -->
                            <div class="matrix-column-headers">
                                <div
                                    v-for="(item, index) in data"
                                    :key="'col-' + index"
                                    class="column-header"
                                    :class="{ active: selectedColumn === index }"
                                    @click="handleColumnClick(index)"
                                    @mouseenter="handleColumnHover(index)"
                                    @mouseleave="handleColumnLeave"
                                >
                                    {{ item.symbol }}
                                </div>
                            </div>

                            <!-- Correlation Cells -->
                            <div class="matrix-cells">
                                <div v-for="(rowItem, rowIndex) in data" :key="rowIndex" class="matrix-row">
                                    <div
                                        v-for="(cellValue, colIndex) in rowItem.correlations"
                                        :key="colIndex"
                                        class="matrix-cell"
                                        :class="getCellClass(cellValue)"
                                        :style="{ background: getCellColor(cellValue) }"
                                        @click="handleCellClick(rowIndex, colIndex, cellValue)"
                                        @mouseenter="handleCellHover(rowIndex, colIndex, cellValue)"
                                        @mouseleave="handleCellLeave"
                                    >
                                        {{ formatCorrelation(cellValue) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tooltip -->
                    <div
                        v-if="tooltip.visible"
                        class="matrix-tooltip"
                        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
                    >
                        <div class="tooltip-symbols">
                            <span class="symbol-a">{{ tooltip.symbolA }}</span>
                            <span class="separator">×</span>
                            <span class="symbol-b">{{ tooltip.symbolB }}</span>
                        </div>
                        <div class="tooltip-correlation">
                            <span class="correlation-label">相关性系数:</span>
                            <span class="correlation-value" :class="getCorrelationClass(tooltip.value)">
                                {{ formatCorrelation(tooltip.value) }}
                            </span>
                        </div>
                        <div class="tooltip-interpretation">
                            {{ interpretCorrelation(tooltip.value) }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Legend -->
            <div class="matrix-legend">
                <div class="legend-title">相关强度 / CORRELATION STRENGTH</div>
                <div class="legend-gradient">
                    <span class="legend-label">-1.0</span>
                    <div class="gradient-bar"></div>
                    <span class="legend-label">+1.0</span>
                </div>
                <div class="legend-labels">
                    <span class="legend-item strong-neg">强负相关</span>
                    <span class="legend-item weak">弱相关</span>
                    <span class="legend-item strong-pos">强正相关</span>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'
    import ArtDecoButton from '../base/ArtDecoButton.vue'
    import ArtDecoLoader from '../trading/ArtDecoLoader.vue'

    // ============================================
    //   类型定义
    // ============================================

    interface CorrelationData {
        symbol: string
        name?: string
        correlations: number[]
    }

    interface Props {
        title?: string
        subtitle?: string
        data: CorrelationData[]
        loading?: boolean
    }

    // ============================================
    //   Props & Emits
    // ============================================

    const props = withDefaults(defineProps<Props>(), {
        title: '相关性矩阵',
        subtitle: 'CORRELATION MATRIX',
        loading: false
    })

    const emit = defineEmits<{
        refresh: []
        cellClick: [rowIndex: number, colIndex: number, value: number]
    }>()

    // ============================================
    //   响应式数据
    // ============================================

    const selectedRow = ref<number | null>(null)
    const selectedColumn = ref<number | null>(null)
    const tooltip = ref({
        visible: false,
        x: 0,
        y: 0,
        symbolA: '',
        symbolB: '',
        value: 0
    })

    // ============================================
    //   工具函数
    // ============================================

    const formatCorrelation = (value: number) => {
        return value.toFixed(3)
    }

    const getCellClass = (value: number) => {
        const absValue = Math.abs(value)
        if (absValue >= 0.7) return 'strong'
        if (absValue >= 0.4) return 'moderate'
        if (absValue >= 0.2) return 'weak'
        return 'very-weak'
    }

    const getCellColor = (value: number) => {
        // 红色表示负相关，绿色表示正相关，透明度表示强度
        const absValue = Math.abs(value)
        const opacity = 0.1 + absValue * 0.9 // 0.1 to 1.0
        const colorStrength = `${(opacity * 100).toFixed(1)}%`

        if (value > 0) {
            // 正相关 - 绿色
            return `color-mix(in srgb, var(--artdeco-rise) ${colorStrength}, transparent)`
        } else {
            // 负相关 - 红色
            return `color-mix(in srgb, var(--artdeco-fall) ${colorStrength}, transparent)`
        }
    }

    const getCorrelationClass = (value: number) => {
        if (value > 0.7) return 'strong-pos'
        if (value > 0.3) return 'moderate-pos'
        if (value < -0.7) return 'strong-neg'
        if (value < -0.3) return 'moderate-neg'
        return 'neutral'
    }

    const interpretCorrelation = (value: number) => {
        const absValue = Math.abs(value)
        let strength = ''
        if (absValue >= 0.9) strength = '极强'
        else if (absValue >= 0.7) strength = '强'
        else if (absValue >= 0.4) strength = '中等'
        else if (absValue >= 0.2) strength = '弱'
        else strength = '极弱'

        const direction = value > 0 ? '正' : value < 0 ? '负' : '无'
        return `${direction}相关 (${strength})`
    }

    // ============================================
    //   交互处理
    // ============================================

    const handleRowClick = (index: number) => {
        selectedRow.value = index
        selectedColumn.value = null
    }

    const handleColumnClick = (index: number) => {
        selectedColumn.value = index
        selectedRow.value = null
    }

    const handleRowHover = (_index: number) => {
        // 高亮行
    }

    const handleRowLeave = () => {
        // 取消高亮
    }

    const handleColumnHover = (_index: number) => {
        // 高亮列
    }

    const handleColumnLeave = () => {
        // 取消高亮
    }

    const handleCellClick = (rowIndex: number, colIndex: number, value: number) => {
        selectedRow.value = rowIndex
        selectedColumn.value = colIndex
        emit('cellClick', rowIndex, colIndex, value)
    }

    const handleCellHover = (rowIndex: number, colIndex: number, value: number) => {
        if (!props.data[rowIndex] || !props.data[colIndex]) return

        const event = window.event as MouseEvent
        if (!event) return

        tooltip.value = {
            visible: true,
            x: event.clientX + 15,
            y: event.clientY + 15,
            symbolA: props.data[rowIndex].symbol,
            symbolB: props.data[colIndex].symbol,
            value: value
        }
    }

    const handleCellLeave = () => {
        tooltip.value.visible = false
    }

    const handleRefresh = () => {
        emit('refresh')
    }
</script>

<style scoped lang="scss">
@import "./styles/CorrelationMatrix";
</style>
