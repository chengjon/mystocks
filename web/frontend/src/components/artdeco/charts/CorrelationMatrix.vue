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

        if (value > 0) {
            // 正相关 - 绿色
            return `rgba(0, 230, 118, ${opacity})`
        } else {
            // 负相关 - 红色
            return `rgba(255, 82, 82, ${opacity})`
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

    const handleRowHover = (index: number) => {
        // 高亮行
    }

    const handleRowLeave = () => {
        // 取消高亮
    }

    const handleColumnHover = (index: number) => {
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
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   ART DECO CORRELATION MATRIX
    // ============================================

    .artdeco-correlation-matrix {
        width: 100%;
    }

    // ============================================
    //   MATRIX HEADER
    // ============================================

    .matrix-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: var(--artdeco-spacing-6);
        padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);

        .header-title {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .title-icon {
                font-size: var(--artdeco-text-2xl);
                opacity: 0.8;
            }

            .title-text {
                .title-main {
                    font-family: var(--artdeco-font-heading);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 700;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    line-height: var(--artdeco-leading-tight);
                }

                .title-sub {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-text-xs);
                    font-weight: 600;
                    color: var(--artdeco-fg-muted);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin-top: var(--artdeco-spacing-1);
                }
            }
        }
    }

    // ============================================
    //   MATRIX CONTAINER
    // ============================================

    .matrix-container {
        position: relative;
        min-height: 500px;
        padding: var(--artdeco-spacing-6);

        &.loading {
            display: flex;
            align-items: center;
            justify-content: center;
        }
    }

    .matrix-content {
        position: relative;
    }

    // ============================================
    //   EMPTY STATE
    // ============================================

    .empty-state {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;

        .empty-icon {
            font-size: var(--artdeco-text-5xl);
            margin-bottom: var(--artdeco-spacing-4);
            opacity: 0.3;
        }

        .empty-text {
            font-family: var(--artdeco-font-heading);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            margin-bottom: var(--artdeco-spacing-2);
        }

        .empty-hint {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-dim);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    // ============================================
    //   MATRIX WRAPPER
    // ============================================

    .matrix-wrapper {
        display: flex;
        gap: var(--artdeco-spacing-4);
        max-height: 600px;
        overflow: auto;
        padding: var(--artdeco-spacing-4);
        background: rgba(212, 175, 55, 0.02);
        border: 1px solid var(--artdeco-gold-dim);
        border-radius: 8px;
    }

    // Row Headers
    .matrix-row-headers {
        display: flex;
        flex-direction: column;
        gap: 2px;

        .row-header {
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: var(--artdeco-spacing-3);
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            cursor: pointer;
            transition: all var(--artdeco-transition-default);
            border-right: 2px solid transparent;

            &:hover {
                color: var(--artdeco-gold-primary);
                background: rgba(212, 175, 55, 0.1);
            }

            &.active {
                color: var(--artdeco-gold-primary);
                border-right-color: var(--artdeco-gold-primary);
                background: rgba(212, 175, 55, 0.15);
            }
        }
    }

    // Matrix Grid
    .matrix-grid {
        display: flex;
        flex-direction: column;
    }

    // Column Headers
    .matrix-column-headers {
        display: flex;
        gap: 2px;
        margin-bottom: var(--artdeco-spacing-2);
        margin-left: 60px; // Align with cells

        .column-header {
            width: 40px;
            height: 60px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding-bottom: var(--artdeco-spacing-2);
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            cursor: pointer;
            transition: all var(--artdeco-transition-default);
            border-bottom: 2px solid transparent;
            writing-mode: vertical-rl;
            text-orientation: mixed;

            &:hover {
                color: var(--artdeco-gold-primary);
                background: rgba(212, 175, 55, 0.1);
            }

            &.active {
                color: var(--artdeco-gold-primary);
                border-bottom-color: var(--artdeco-gold-primary);
                background: rgba(212, 175, 55, 0.15);
            }
        }
    }

    // Matrix Cells
    .matrix-cells {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .matrix-row {
        display: flex;
        gap: 2px;
    }

    .matrix-cell {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 700;
        cursor: pointer;
        transition: all var(--artdeco-transition-default);
        border: 1px solid rgba(212, 175, 55, 0.2);
        color: var(--artdeco-fg-primary);

        &:hover {
            transform: scale(1.1);
            border-color: var(--artdeco-gold-primary);
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
            z-index: 10;
        }

        // Cell intensity classes
        &.strong {
            color: #fff;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }

        &.moderate {
            color: var(--artdeco-fg-primary);
        }

        &.weak {
            color: var(--artdeco-fg-muted);
        }

        &.very-weak {
            color: var(--artdeco-fg-dim);
        }
    }

    // ============================================
    //   TOOLTIP
    // ============================================

    .matrix-tooltip {
        position: fixed;
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-gold-dim);
        padding: var(--artdeco-spacing-4);
        border-radius: 4px;
        pointer-events: none;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        min-width: 200px;

        .tooltip-symbols {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--artdeco-spacing-2);
            margin-bottom: var(--artdeco-spacing-3);
            padding-bottom: var(--artdeco-spacing-3);
            border-bottom: 1px solid var(--artdeco-gold-dim);

            .symbol-a,
            .symbol-b {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                font-weight: 700;
                color: var(--artdeco-gold-primary);
            }

            .separator {
                color: var(--artdeco-fg-muted);
            }
        }

        .tooltip-correlation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-2);

            .correlation-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
            }

            .correlation-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-lg);
                font-weight: 700;

                &.strong-pos,
                &.moderate-pos {
                    color: var(--artdeco-rise);
                }

                &.strong-neg,
                &.moderate-neg {
                    color: var(--artdeco-fall);
                }

                &.neutral {
                    color: var(--artdeco-fg-muted);
                }
            }
        }

        .tooltip-interpretation {
            text-align: center;
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    // ============================================
    //   LEGEND
    // ============================================

    .matrix-legend {
        padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
        border-top: 1px solid var(--artdeco-gold-dim);

        .legend-title {
            font-family: var(--artdeco-font-heading);
            font-size: var(--artdeco-text-xs);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-widest);
            text-align: center;
            margin-bottom: var(--artdeco-spacing-4);
        }

        .legend-gradient {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--artdeco-spacing-4);
            margin-bottom: var(--artdeco-spacing-3);

            .legend-label {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                color: var(--artdeco-fg-muted);
            }

            .gradient-bar {
                width: 200px;
                height: 12px;
                background: linear-gradient(
                    to right,
                    rgba(255, 82, 82, 1) 0%,
                    rgba(255, 82, 82, 0.1) 50%,
                    rgba(0, 230, 118, 0.1) 50%,
                    rgba(0, 230, 118, 1) 100%
                );
                border: 1px solid var(--artdeco-gold-dim);
                border-radius: 2px;
            }
        }

        .legend-labels {
            display: flex;
            justify-content: space-around;

            .legend-item {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);

                &.strong-neg {
                    color: var(--artdeco-fall);
                }

                &.weak {
                    color: var(--artdeco-fg-muted);
                }

                &.strong-pos {
                    color: var(--artdeco-rise);
                }
            }
        }
    }
</style>
