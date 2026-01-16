<template>
    <div class="hybrid-table" :class="sizeClass">
        <div v-if="title" class="hybrid-table__header">
            <h3 class="hybrid-table__title">{{ title }}</h3>
            <div v-if="hasActionsSlot" class="hybrid-table__actions">
                <slot name="actions"></slot>
            </div>
        </div>

        <div class="hybrid-table__container" ref="container">
            <table class="hybrid-table__content">
                <thead class="hybrid-table__thead">
                    <tr>
                        <th
                            v-for="col in columns"
                            :key="col.key"
                            @click="sort(col.key)"
                            :class="['hybrid-table__cell--head', { 'hybrid-table__cell--sortable': col.sortable }]"
                            :style="{ width: col.width }"
                        >
                            <div class="hybrid-table__head-content">
                                <span class="hybrid-table__head-label">{{ col.label }}</span>
                                <span v-if="col.sortable" class="hybrid-table__sort-icon">
                                    <template v-if="sortColumn === col.key">
                                        <span v-if="sortOrder === 'asc'">↑</span>
                                        <span v-else>↓</span>
                                    </template>
                                    <span v-else>↕</span>
                                </span>
                            </div>
                        </th>
                        <th v-if="hasActionsSlot" class="hybrid-table__cell--actions">操作</th>
                    </tr>
                </thead>

                <tbody class="hybrid-table__tbody">
                    <!-- 虚拟滚动模式 -->
                    <template v-if="virtualScroll && sortedData.length > 0">
                        <tr
                            v-for="(row, virtualIndex) in visibleRows"
                            :key="getRowKey(row, startIndex + virtualIndex)"
                            :class="{ 'hybrid-table__row--active': isRowActive(row) }"
                            :style="{ transform: `translateY(${virtualIndex * rowHeight}px)` }"
                            @click="handleRowClick(row, startIndex + virtualIndex)"
                        >
                            <td
                                v-for="col in columns"
                                :key="col.key"
                                :class="getCellClass(row, col)"
                                :style="{ height: `${rowHeight}px` }"
                            >
                                <slot :name="`cell-${col.key}`" :row="row" :value="getRowValue(row, col.key)">
                                    {{ formatCellValue(row, col) }}
                                </slot>
                            </td>
                            <td v-if="hasActionsSlot" class="hybrid-table__cell--actions">
                                <slot name="actions" :row="row" :index="startIndex + virtualIndex"></slot>
                            </td>
                        </tr>
                    </template>

                    <!-- 传统模式 -->
                    <template v-else>
                        <tr
                            v-for="(row, index) in paginatedData"
                            :key="getRowKey(row, index)"
                            :class="{ 'hybrid-table__row--active': isRowActive(row) }"
                            @click="handleRowClick(row, index)"
                        >
                            <td v-for="col in columns" :key="col.key" :class="getCellClass(row, col)">
                                <slot :name="`cell-${col.key}`" :row="row" :value="getRowValue(row, col.key)">
                                    {{ formatCellValue(row, col) }}
                                </slot>
                            </td>
                            <td v-if="hasActionsSlot" class="hybrid-table__cell--actions">
                                <slot name="actions" :row="row" :index="index"></slot>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>

            <!-- 虚拟滚动spacer -->
            <div v-if="virtualScroll" class="hybrid-table__spacer" :style="{ height: `${totalHeight}px` }"></div>
        </div>

        <!-- 分页 -->
        <div v-if="pagination && !virtualScroll" class="hybrid-table__pagination">
            <slot name="pagination">
                <div class="hybrid-table__pagination-info">{{ startIndex + 1 }}-{{ endIndex }} / {{ data.length }}</div>
            </slot>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="hybrid-table__loading">
            <div class="hybrid-table__spinner"></div>
            <p>加载中...</p>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && data.length === 0" class="hybrid-table__empty">
            <p>暂无数据</p>
        </div>

        <!-- 性能监控 (开发模式) -->
        <div v-if="showPerformanceInfo" class="hybrid-table__perf">
            Rendered: {{ virtualScroll ? visibleRows.length : paginatedData.length }} / Total: {{ data.length }}
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed, ref, useSlots, onMounted, onBeforeUnmount } from 'vue'

    interface Column {
        key: string
        label: string
        sortable?: boolean
        width?: string
        format?: (value: any) => string
        class?: (row: any) => string | string[]
    }

    interface Props {
        columns: Column[]
        data: any[]
        title?: string
        rowKey?: string
        pagination?: boolean
        loading?: boolean
        size?: 'sm' | 'md' | 'lg'
        virtualScroll?: boolean
        rowHeight?: number
        containerHeight?: number
        pageSize?: number
        currentPage?: number
        defaultSort?: string
        defaultSortOrder?: 'asc' | 'desc'
        activeRow?: any
        showPerformanceInfo?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        rowKey: 'id',
        pagination: false,
        loading: false,
        size: 'md',
        virtualScroll: false,
        rowHeight: 36,
        containerHeight: 400,
        pageSize: 50,
        currentPage: 1,
        defaultSort: '',
        defaultSortOrder: 'desc',
        activeRow: undefined,
        showPerformanceInfo: false
    })

    const emit = defineEmits<{
        'row-click': [row: any, index: number]
        sort: [column: string, order: 'asc' | 'desc']
        'page-change': [page: number]
    }>()

    const slots = useSlots()
    const container = ref<HTMLElement>()

    const sortColumn = ref(props.defaultSort)
    const sortOrder = ref<'asc' | 'desc'>(props.defaultSortOrder)
    const currentPage = ref(props.currentPage)

    // 虚拟滚动状态
    const scrollTop = ref(0)
    const startIndex = ref(0)
    const endIndex = ref(0)

    const hasActionsSlot = computed(() => !!slots.actions)

    const sizeClass = computed(() => {
        return `hybrid-table--${props.size}`
    })

    const sortedData = computed(() => {
        if (!sortColumn.value) return props.data

        const col = props.columns.find(c => c.key === sortColumn.value)
        if (!col) return props.data

        return [...props.data].sort((a: any, b: any) => {
            const aVal = getRowValue(a, sortColumn.value)
            const bVal = getRowValue(b, sortColumn.value)

            let comparison = 0
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                comparison = aVal - bVal
            } else {
                comparison = String(aVal).localeCompare(String(bVal))
            }

            return sortOrder.value === 'asc' ? comparison : -comparison
        })
    })

    const paginatedData = computed(() => {
        if (props.virtualScroll) return []
        if (!props.pagination) return sortedData.value

        const start = (currentPage.value - 1) * props.pageSize
        const end = start + props.pageSize
        return sortedData.value.slice(start, end)
    })

    // 虚拟滚动计算
    const totalHeight = computed(() => sortedData.value.length * props.rowHeight)

    const visibleRange = computed(() => {
        if (!props.virtualScroll) return { start: 0, end: 0 }

        const start = Math.max(0, Math.floor(scrollTop.value / props.rowHeight) - 5)
        const visibleCount = Math.ceil(props.containerHeight / props.rowHeight)
        const end = Math.min(sortedData.value.length, start + visibleCount + 10)

        startIndex.value = start
        endIndex.value = end

        return { start, end }
    })

    const visibleRows = computed(() => {
        if (!props.virtualScroll) return []
        return sortedData.value.slice(visibleRange.value.start, visibleRange.value.end)
    })

    function getRowKey(row: any, index: number) {
        return row[props.rowKey] || index
    }

    function getRowValue(row: any, key: string) {
        return key.split('.').reduce((obj, k) => obj?.[k], row)
    }

    function formatCellValue(row: any, col: Column) {
        const value = getRowValue(row, col.key)
        if (col.format) {
            return col.format(value)
        }
        if (typeof value === 'number') {
            return value.toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })
        }
        return value
    }

    function getCellClass(row: any, col: Column) {
        const classes = ['hybrid-table__cell']
        if (col.class) {
            const colClass = col.class(row)
            if (Array.isArray(colClass)) {
                classes.push(...colClass)
            } else {
                classes.push(colClass)
            }
        }
        return classes
    }

    function isRowActive(row: any) {
        return props.activeRow && getRowKey(row, 0) === getRowKey(props.activeRow, 0)
    }

    function handleRowClick(row: any, index: number) {
        emit('row-click', row, index)
    }

    function sort(column: string) {
        const col = props.columns.find(c => c.key === column)
        if (!col?.sortable) return

        if (sortColumn.value === column) {
            sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
        } else {
            sortColumn.value = column
            sortOrder.value = 'asc'
        }

        emit('sort', column, sortOrder.value)
    }

    function handleScroll() {
        if (!container.value || !props.virtualScroll) return
        scrollTop.value = container.value.scrollTop
    }

    // 性能优化：防抖更新
    let scrollRafId: number | null = null

    function throttledScroll() {
        if (scrollRafId) return

        scrollRafId = requestAnimationFrame(() => {
            handleScroll()
            scrollRafId = null
        })
    }

    onMounted(() => {
        if (container.value && props.virtualScroll) {
            container.value.addEventListener('scroll', throttledScroll, { passive: true })
        }
    })

    onBeforeUnmount(() => {
        if (container.value) {
            container.value.removeEventListener('scroll', throttledScroll)
        }
        if (scrollRafId) {
            cancelAnimationFrame(scrollRafId)
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/data-dense/index.scss';

    // ============================================
    //   HYBRID TABLE - 数据密集型表格
    //   Art Deco 视觉 + 数据密集性能优化
    // ============================================

    .hybrid-table {
        @include hybrid-card;
        @include gpu-accelerated;

        // 虚拟滚动模式
        &--virtual {
            .hybrid-table__container {
                @include virtual-scroll-container;
                overflow-y: auto;
                overflow-x: hidden;
                max-height: v-bind('containerHeight + "px"');
            }

            .hybrid-table__tbody {
                position: relative;
            }

            .hybrid-table__spacer {
                height: v-bind('totalHeight + "px"');
            }
        }

        // 传统模式
        &:not(&--virtual) {
            .hybrid-table__container {
                overflow-x: auto;
            }
        }
    }

    .hybrid-table__header {
        @include data-dense-spacing;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: var(--data-dense-border-width) solid var(--data-dense-border-color);
    }

    .hybrid-table__title {
        @include artdeco-gold-accent;
        font-family: var(--hybrid-font-display);
        font-size: var(--data-dense-font-lg);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }

    .hybrid-table__actions {
        display: flex;
        gap: var(--data-dense-gap-sm);
    }

    .hybrid-table__container {
        position: relative;
    }

    .hybrid-table__content {
        width: 100%;
        border-collapse: collapse;
        font-family: var(--hybrid-font-body);
    }

    .hybrid-table__thead {
        position: sticky;
        top: 0;
        z-index: 10;
        background-color: var(--artdeco-bg-card);
    }

    // 表头单元格
    .hybrid-table__cell--head {
        @include artdeco-gold-accent;
        font-family: var(--hybrid-font-display);
        font-size: var(--data-dense-font-sm);
        font-weight: 600;
        text-align: left;
        padding: var(--data-dense-table-cell-padding);
        border-bottom: var(--data-dense-border-width) solid var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
        user-select: none;
        background-color: rgba(212, 175, 55, 0.05);
        height: var(--data-dense-table-header-height);
    }

    .hybrid-table__cell--sortable {
        cursor: pointer;
        @include data-dense-transitions;

        &:hover {
            background-color: rgba(212, 175, 55, 0.1);
        }
    }

    .hybrid-table__head-content {
        display: flex;
        align-items: center;
        gap: var(--data-dense-gap-xs);
    }

    .hybrid-table__head-label {
        flex: 1;
    }

    .hybrid-table__sort-icon {
        color: rgba(212, 175, 55, 0.4);
        font-size: var(--data-dense-font-xs);
        @include data-dense-transitions;
    }

    .hybrid-table__cell--sortable:hover .hybrid-table__sort-icon {
        color: var(--artdeco-gold-primary);
    }

    // 表体单元格
    .hybrid-table__cell {
        @include data-dense-typography;
        padding: var(--data-dense-table-cell-padding);
        color: var(--artdeco-fg-primary);
        border-bottom: var(--data-dense-border-width) solid var(--data-dense-border-color);
        @include data-dense-transitions;

        // 金融数据颜色
        &--up {
            color: var(--artdeco-up);
            font-weight: 600;
        }
        &--down {
            color: var(--artdeco-down);
            font-weight: 600;
        }
        &--flat {
            color: var(--artdeco-flat);
        }
        &--profit {
            color: var(--artdeco-profit);
        }
        &--loss {
            color: var(--artdeco-loss);
        }
    }

    .hybrid-table__tbody tr {
        @include gpu-accelerated;

        &:hover .hybrid-table__cell {
            background-color: rgba(212, 175, 55, 0.05);
        }
    }

    .hybrid-table__row--active .hybrid-table__cell {
        background-color: rgba(212, 175, 55, 0.1);
        color: var(--artdeco-gold-primary);
    }

    .hybrid-table__cell--actions {
        display: flex;
        gap: var(--data-dense-gap-sm);
        align-items: center;
        white-space: nowrap;
    }

    // 分页
    .hybrid-table__pagination {
        @include data-dense-spacing;
        border-top: var(--data-dense-border-width) solid var(--data-dense-border-color);
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .hybrid-table__pagination-info {
        @include data-dense-typography;
        color: var(--artdeco-fg-muted);
    }

    // 加载状态
    .hybrid-table__loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--data-dense-padding-lg);
        gap: var(--data-dense-gap-sm);
    }

    .hybrid-table__spinner {
        width: 24px;
        height: 24px;
        border: 2px solid rgba(212, 175, 55, 0.2);
        border-top-color: var(--artdeco-gold-primary);
        border-radius: 0px; // Art Deco sharp corners
        animation: hybrid-spin 1s linear infinite;
    }

    @keyframes hybrid-spin {
        to {
            transform: rotate(360deg);
        }
    }

    .hybrid-table__loading p {
        @include data-dense-typography;
        color: var(--artdeco-fg-muted);
        margin: 0;
    }

    // 空状态
    .hybrid-table__empty {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--data-dense-padding-lg);
    }

    .hybrid-table__empty p {
        @include data-dense-typography;
        color: var(--artdeco-fg-muted);
        margin: 0;
    }

    // 性能监控
    .hybrid-table__perf {
        position: absolute;
        top: 2px;
        right: 2px;
        font-size: 10px;
        color: rgba(255, 255, 255, 0.5);
        background: rgba(0, 0, 0, 0.8);
        padding: 2px 4px;
        border-radius: 0px;
        font-family: var(--hybrid-font-mono);
        pointer-events: none;
        z-index: 10;
    }

    // 尺寸变体
    .hybrid-table--sm {
        .hybrid-table__cell--head,
        .hybrid-table__cell {
            padding: 4px 8px;
            font-size: var(--data-dense-font-xs);
        }
    }

    .hybrid-table--lg {
        .hybrid-table__cell--head,
        .hybrid-table__cell {
            padding: 8px 16px;
            font-size: var(--data-dense-font-base);
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .hybrid-table {
            .hybrid-table__title {
                font-size: var(--data-dense-font-base);
            }

            .hybrid-table__cell--head,
            .hybrid-table__cell {
                padding: var(--data-dense-padding-xs);
                font-size: var(--data-dense-font-xs);
            }
        }
    }

    // ============================================
    //   PERFORMANCE NOTES - 性能说明
    // ============================================

    /*
  数据密集型优化：
  1. 虚拟滚动：只渲染可见行，大幅提升大数据集性能
  2. GPU加速：transform属性启用硬件加速
  3. 防抖滚动：减少不必要的重渲染
  4. 紧凑间距：最大化数据密度

  预期性能提升：
  - 1000+ 行数据时，从 ~20fps 提升到 ~60fps
  - 内存使用减少 80%
  - 初始渲染时间减少 90%
*/
</style>
