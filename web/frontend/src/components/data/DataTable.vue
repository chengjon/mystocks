<template>
  <div class="data-table-wrapper">
    <!-- Header -->
    <div v-if="title" class="data-table-header">
      <h3>{{ title }}</h3>
      <div v-if="$slots.actions" class="data-table-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Table -->
    <div class="data-table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th
              v-for="(col, _idx) in columns"
              :key="col.key"
              @click="sort(col.key)"
              :class="{ sortable: col.sortable }"
            >
              <span class="table-th-label">{{ col.label }}</span>
              <span v-if="col.sortable" class="table-sort-icon">
                <template v-if="sortColumn === col.key">
                  <span v-if="sortOrder === 'asc'">↑</span>
                  <span v-else>↓</span>
                </template>
                <span v-else>↕</span>
              </span>
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="(row, index) in sortedData"
            :key="getRowKey(row, index)"
            :class="{ active: isRowActive(row) }"
            @click="handleRowClick(row, index)"
          >
            <td
              v-for="(col, _idx) in columns"
              :key="col.key"
              :class="getCellClass(row, col)"
            >
              <slot
                :name="`cell-${col.key}`"
                :row="row"
                :value="getRowValue(row, col.key)"
              >
                {{ formatCellValue(row, col) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="pagination" class="data-table-pagination">
      <slot name="pagination">
        <div class="pagination-info">
          共 {{ data.length }} 条记录
        </div>
      </slot>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="data-table-loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Empty -->
    <div v-if="!loading && data.length === 0" class="data-table-empty">
      <p>暂无数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, useSlots } from 'vue'

interface Column {
  key: string
  label: string
  sortable?: boolean
  format?: (value: unknown) => string
  class?: (row: unknown) => string | string[]
}

interface Props {
  columns: Column[]
  data: Record<string, unknown>[]
  title?: string
  rowKey?: string
  pagination?: boolean
  loading?: boolean
  size?: 'sm' | 'md' | 'lg'
  defaultSort?: string
  defaultSortOrder?: 'asc' | 'desc'
  activeRow?: Record<string, unknown>
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  rowKey: 'id',
  pagination: false,
  loading: false,
  size: 'md',
  defaultSort: '',
  defaultSortOrder: 'desc',
  activeRow: undefined
})

const emit = defineEmits<{
  'row-click': [row: Record<string, unknown>, index: number]
  'sort': [column: string, order: 'asc' | 'desc']
}>()

const _slots = useSlots()

const sortColumn = ref(props.defaultSort)
const sortOrder = ref<'asc' | 'desc'>(props.defaultSortOrder)

const sortedData = computed(() => {
  if (!sortColumn.value) return props.data

  const col = props.columns.find(c => c.key === sortColumn.value)
  if (!col) return props.data

  return [...props.data].sort((a, b) => {
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

function getRowKey(row: Record<string, unknown>, index: number): string | number {
  const key = row[props.rowKey]
  return (typeof key === 'string' || typeof key === 'number') ? key : index
}

function getRowValue(row: Record<string, unknown>, key: string): unknown {
  return key.split('.').reduce((obj: Record<string, unknown> | undefined, k) => obj?.[k] as Record<string, unknown> | undefined, row)
}

function formatCellValue(row: Record<string, unknown>, col: Column) {
  const value = getRowValue(row, col.key)
  if (col.format) {
    return col.format(value)
  }
  if (typeof value === 'number') {
    return (value as number).toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }
  return value
}

function getCellClass(row: Record<string, unknown>, col: Column) {
  const classes = []
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

function isRowActive(row: Record<string, unknown>) {
  return props.activeRow && getRowKey(row, 0) === getRowKey(props.activeRow, 0)
}

function handleRowClick(row: Record<string, unknown>, index: number) {
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
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.data-table-wrapper {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  overflow: hidden;
}

.data-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.data-table-header h3 {
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-compact-base);
  font-weight: var(--artdeco-font-semibold);
  color: var(--artdeco-gold-primary);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  margin: 0;
}

.data-table-actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.data-table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-compact-sm);
}

.data-table thead th {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-compact-sm);
  font-weight: var(--artdeco-font-semibold);
  text-align: left;
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-gold-opacity-30);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  white-space: nowrap;
  user-select: none;
}

.data-table thead th.sortable {
  cursor: pointer;
  transition:
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out);
}

.data-table thead th.sortable:hover {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
}

.table-th-label {
  flex: 1;
}

.table-sort-icon {
  color: color-mix(in srgb, var(--artdeco-gold-primary) 45%, transparent);
  font-size: var(--artdeco-text-compact-sm);
  transition: color var(--artdeco-transition-quick) var(--artdeco-ease-out);
}

.data-table thead th.sortable:hover .table-sort-icon {
  color: var(--artdeco-gold-light);
}

.data-table tbody td {
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-compact-sm);
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-border-default) 65%, transparent);
  transition:
    background var(--artdeco-transition-quick) var(--artdeco-ease-out),
    color var(--artdeco-transition-quick) var(--artdeco-ease-out);
}

.data-table tbody tr:hover td {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
}

.data-table tbody tr.active td {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
  color: var(--artdeco-gold-primary);
}

.data-table tbody td.data-rise {
  color: var(--artdeco-rise);
  font-weight: var(--artdeco-font-semibold);
}

.data-table tbody td.data-fall {
  color: var(--artdeco-down);
  font-weight: var(--artdeco-font-semibold);
}

.data-table tbody td.data-flat {
  color: var(--artdeco-fg-muted);
}

.data-table-pagination {
  padding: var(--artdeco-spacing-3);
  border-top: 1px solid var(--artdeco-border-default);
  display: flex;
  justify-content: center;
  align-items: center;
}

.pagination-info {
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-compact-sm);
  color: var(--artdeco-fg-muted);
}

.data-table-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-12);
  gap: var(--artdeco-spacing-4);
}

.loading-spinner {
  width: var(--artdeco-spacing-8);
  height: var(--artdeco-spacing-8);
  border: calc(var(--artdeco-spacing-3) / 4) solid color-mix(in srgb, var(--artdeco-border-default) 70%, transparent);
  border-top-color: var(--artdeco-gold-primary);
  border-radius: var(--artdeco-radius-none);
  animation: spin 1s linear infinite;
  box-shadow: 0 0 var(--artdeco-spacing-3) color-mix(in srgb, var(--artdeco-gold-primary) 22%, transparent);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.data-table-loading p {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-sm);
  color: var(--artdeco-fg-muted);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  margin: 0;
}

.data-table-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-12);
}

.data-table-empty p {
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-sm);
  color: var(--artdeco-fg-muted);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  margin: 0;
}
</style>
