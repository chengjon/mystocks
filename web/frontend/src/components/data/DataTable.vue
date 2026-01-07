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
              v-for="col in columns"
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
              v-for="col in columns"
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
  defaultSort?: string
  defaultSortOrder?: 'asc' | 'desc'
  activeRow?: any
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
  'row-click': [row: any, index: number]
  'sort': [column: string, order: 'asc' | 'desc']
}>()

const slots = useSlots()

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
</script>

<style scoped lang="scss">
.data-table-wrapper {
  background: #0A0A0A;
  border: 1px solid #1A1A1A;
  border-radius: 4px;
  overflow: hidden;
}

.data-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #1A1A1A;
}

.data-table-header h3 {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #E5E5E5;
  margin: 0;
}

.data-table-actions {
  display: flex;
  gap: 8px;
}

.data-table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px; // 紧凑字体
}

.data-table thead th {
  background: #141414;
  color: #E5E5E5;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  font-weight: 600;
  text-align: left;
  padding: 8px 12px; // 紧凑padding
  border-bottom: 1px solid #2A2A2A;
  text-transform: none;
  white-space: nowrap;
  user-select: none;
}

.data-table thead th.sortable {
  cursor: pointer;
  transition: background 150ms ease;
}

.data-table thead th.sortable:hover {
  background: #1A1A1A;
}

.data-table thead th:first-child {
  border-top-left-radius: 4px;
}

.data-table thead th:last-child {
  border-top-right-radius: 4px;
}

.table-th-label {
  flex: 1;
}

.table-sort-icon {
  color: #666666;
  font-size: 12px;
  transition: color 150ms ease;
}

.data-table thead th.sortable:hover .table-sort-icon {
  color: #A0A0A0;
}

.data-table tbody td {
  padding: 8px 12px; // 紧凑padding
  color: #E5E5E5;
  font-size: 12px;
  border-bottom: 1px solid #1A1A1A;
  transition: background 150ms ease;
}

.data-table tbody tr:hover td {
  background: #0F0F0F;
}

.data-table tbody tr.active td {
  background: #1A1A1A;
  color: #3B82F6;
}

// Data color classes
.data-table tbody td.data-rise {
  color: #FF5252;
  font-weight: 600;
}

.data-table tbody td.data-fall {
  color: #00E676;
  font-weight: 600;
}

.data-table tbody td.data-flat {
  color: #666666;
}

.data-table-pagination {
  padding: 12px;
  border-top: 1px solid #1A1A1A;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pagination-info {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: #A0A0A0;
}

// Loading state
.data-table-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 16px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #1A1A1A;
  border-top-color: #3B82F6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.data-table-loading p {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  color: #A0A0A0;
  margin: 0;
}

// Empty state
.data-table-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.data-table-empty p {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  color: #666666;
  margin: 0;
}
</style>
