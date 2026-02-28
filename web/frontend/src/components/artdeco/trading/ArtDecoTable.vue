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
                            v-for="(col, _idx) in columns"
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
                                v-for="(col, _idx) in columns"
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
        format?: (value: unknown) => string
        class?: (row: unknown) => string | string[]
    }

    interface Props {
        columns?: Column[]
        data: unknown[]
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
        activeRow?: unknown
        showPerformanceInfo?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        columns: () => [],
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
        'row-click': [row: unknown, index: number]
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

        return [...props.data].sort((a: unknown, b: unknown) => {
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

    function getRowKey(row: unknown, index: number) {
        return row[props.rowKey] || index
    }

    function getRowValue(row: unknown, key: string) {
        return key.split('.').reduce((obj, k) => obj?.[k], row)
    }

    function formatCellValue(row: unknown, col: Column) {
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

    function getCellClass(row: unknown, col: Column) {
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

    function isRowActive(row: unknown) {
        return props.activeRow && getRowKey(row, 0) === getRowKey(props.activeRow, 0)
    }

    function handleRowClick(row: unknown, index: number) {
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
@import "./styles/ArtDecoTable";
</style>
