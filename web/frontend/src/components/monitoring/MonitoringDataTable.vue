<template>
  <div class="monitoring-data-table fintech-card">
    <div class="table-header" v-if="title || $slots.header">
      <div class="header-info">
        <h3 class="fintech-text-primary table-title" v-if="title">{{ title }}</h3>
        <p class="fintech-text-secondary table-subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="header-actions" v-if="$slots.actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <div class="table-container">
      <table class="fintech-table data-table">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :style="{ width: column.width, textAlign: column.align || 'left' }"
              :class="{ sortable: column.sortable }"
              @click="column.sortable && handleSort(column.key)"
            >
              <div class="header-content">
                <span class="header-text">{{ column.title }}</span>
                <span class="sort-icon" v-if="column.sortable">
                  <component :is="getSortIcon(column.key)" />
                </span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in paginatedData"
            :key="getRowKey(row, index)"
            :class="{ 'row-hover': hoverable, 'row-selected': isSelected(row) }"
            @click="handleRowClick(row, index)"
            @dblclick="handleRowDoubleClick(row, index)"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              :style="{ textAlign: column.align || 'left' }"
              :class="getCellClass(column, row)"
            >
              <slot
                :name="`column-${column.key}`"
                :row="row"
                :column="column"
                :index="index"
                :value="getCellValue(row, column)"
              >
                <span :class="getValueClass(column, row)">
                  {{ formatCellValue(getCellValue(row, column), column) }}
                </span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 空状态 -->
    <div v-if="data.length === 0" class="empty-table">
      <div class="empty-icon">
        <component :is="emptyIcon" />
      </div>
      <div class="empty-content">
        <h4 class="fintech-text-secondary">{{ emptyTitle }}</h4>
        <p class="fintech-text-tertiary">{{ emptyMessage }}</p>
        <slot name="empty-action">
          <button v-if="showRefresh" class="fintech-btn" @click="$emit('refresh')">
            REFRESH DATA
          </button>
        </slot>
      </div>
    </div>

    <!-- 分页器 -->
    <div class="table-footer" v-if="showPagination && totalPages > 1">
      <div class="pagination-info fintech-text-secondary">
        Showing {{ startIndex + 1 }}-{{ endIndex }} of {{ totalCount }} entries
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          ‹
        </button>

        <span
          v-for="page in visiblePages"
          :key="page"
          class="page-number"
          :class="{ active: page === currentPage }"
          @click="goToPage(page)"
        >
          {{ page }}
        </span>

        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          ›
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="table-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text fintech-text-secondary">{{ loadingText }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  DatabaseOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  columns: {
    type: Array,
    required: true,
    validator: (columns) => {
      return columns.every(col => col.key && col.title)
    }
  },
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading data...'
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  hoverable: {
    type: Boolean,
    default: true
  },
  selectable: {
    type: Boolean,
    default: false
  },
  selectedRows: {
    type: Array,
    default: () => []
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  pageSize: {
    type: Number,
    default: 10,
    validator: (value) => value > 0
  },
  showRefresh: {
    type: Boolean,
    default: false
  },
  emptyTitle: {
    type: String,
    default: 'NO DATA'
  },
  emptyMessage: {
    type: String,
    default: 'No data available at this time'
  },
  sortBy: {
    type: String,
    default: ''
  },
  sortOrder: {
    type: String,
    default: 'asc', // 'asc' | 'desc'
    validator: (value) => ['asc', 'desc'].includes(value)
  }
})

const emit = defineEmits([
  'row-click',
  'row-double-click',
  'sort-change',
  'page-change',
  'refresh',
  'selection-change'
])

const currentPage = ref(1)
const currentSortBy = ref(props.sortBy)
const currentSortOrder = ref(props.sortOrder)
const emptyIcon = DatabaseOutlined

// 计算属性
const sortedData = computed(() => {
  if (!currentSortBy.value) return props.data

  return [...props.data].sort((a, b) => {
    const aVal = getCellValue(a, { key: currentSortBy.value })
    const bVal = getCellValue(b, { key: currentSortBy.value })

    let result = 0
    if (aVal < bVal) result = -1
    if (aVal > bVal) result = 1

    return currentSortOrder.value === 'desc' ? -result : result
  })
})

const paginatedData = computed(() => {
  if (!props.showPagination) return sortedData.value

  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return sortedData.value.slice(start, end)
})

const totalCount = computed(() => props.data.length)

const totalPages = computed(() => {
  return Math.ceil(totalCount.value / props.pageSize)
})

const startIndex = computed(() => {
  return (currentPage.value - 1) * props.pageSize
})

const endIndex = computed(() => {
  return Math.min(startIndex.value + props.pageSize, totalCount.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)

    if (current > 4) pages.push('...')

    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }

    if (current < total - 3) pages.push('...')

    if (total > 1) pages.push(total)
  }

  return pages.filter(page => page !== '...' || pages.indexOf(page) === pages.lastIndexOf(page))
})

// 工具函数
const getRowKey = (row, index) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row, index)
  }
  return row[props.rowKey] || index
}

const getCellValue = (row, column) => {
  if (column.dataIndex) {
    return column.dataIndex.split('.').reduce((obj, key) => obj?.[key], row)
  }
  return row[column.key]
}

const getCellClass = (column, row) => {
  const classes = []
  if (column.class) classes.push(column.class)
  return classes
}

const getValueClass = (column, row) => {
  const value = getCellValue(row, column)
  if (column.valueClass) {
    return typeof column.valueClass === 'function'
      ? column.valueClass(value, row, column)
      : column.valueClass
  }
  return ''
}

const formatCellValue = (value, column) => {
  if (column.formatter) {
    return column.formatter(value)
  }

  if (typeof value === 'number') {
    if (column.type === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'CNY'
      }).format(value)
    }
    if (column.type === 'percentage') {
      return `${(value * 100).toFixed(2)}%`
    }
    if (column.precision !== undefined) {
      return value.toFixed(column.precision)
    }
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }

  return value || '-'
}

const getSortIcon = (key) => {
  if (currentSortBy.value !== key) return SortAscendingOutlined
  return currentSortOrder.value === 'asc' ? ArrowUpOutlined : ArrowDownOutlined
}

const isSelected = (row) => {
  return props.selectedRows.some(selected => getRowKey(selected, 0) === getRowKey(row, 0))
}

// 事件处理
const handleSort = (key) => {
  if (currentSortBy.value === key) {
    currentSortOrder.value = currentSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    currentSortBy.value = key
    currentSortOrder.value = 'asc'
  }

  emit('sort-change', {
    sortBy: currentSortBy.value,
    sortOrder: currentSortOrder.value
  })
}

const handleRowClick = (row, index) => {
  emit('row-click', { row, index, key: getRowKey(row, index) })
}

const handleRowDoubleClick = (row, index) => {
  emit('row-double-click', { row, index, key: getRowKey(row, index) })
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    emit('page-change', page)
  }
}

// 监听器
watch(() => props.sortBy, (newVal) => {
  currentSortBy.value = newVal
})

watch(() => props.sortOrder, (newVal) => {
  currentSortOrder.value = newVal
})

watch(() => props.data, () => {
  currentPage.value = 1 // 重置到第一页
})
</script>

<style scoped>
.monitoring-data-table {
  display: flex;
  flex-direction: column;
  background: var(--fintech-bg-secondary);
  border: 1px solid var(--fintech-border-base);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-5);
  border-bottom: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.header-info h3 {
  margin: 0 0 var(--fintech-space-1) 0;
  font-size: var(--fintech-font-size-lg);
  font-weight: 600;
}

.header-info p {
  margin: 0;
  font-size: var(--fintech-font-size-sm);
}

.table-container {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 500px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  position: sticky;
  top: 0;
  z-index: 10;
  padding: var(--fintech-space-3) var(--fintech-space-4);
  font-weight: 600;
  font-size: var(--fintech-font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.02em;
  background: var(--fintech-bg-tertiary);
  border-bottom: 2px solid var(--fintech-border-base);
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: var(--fintech-bg-elevated);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--fintech-space-2);
}

.sort-icon {
  opacity: 0.6;
  transition: opacity var(--fintech-transition-fast);
}

.sortable:hover .sort-icon {
  opacity: 1;
}

.data-table td {
  padding: var(--fintech-space-3) var(--fintech-space-4);
  border-bottom: 1px solid var(--fintech-border-dark);
  font-family: var(--fintech-font-family-data);
  transition: background-color var(--fintech-transition-fast);
}

.data-table tbody tr {
  cursor: pointer;
}

.data-table tbody tr.row-hover:hover {
  background: var(--fintech-bg-tertiary);
}

.data-table tbody tr.row-selected {
  background: var(--fintech-accent-primary);
  color: white;
}

.data-table tbody tr.row-selected .fintech-text-primary {
  color: white !important;
}

.data-table tbody tr.row-selected .fintech-text-secondary {
  color: rgba(255, 255, 255, 0.75) !important;
}

.data-table tbody tr.row-selected .fintech-text-tertiary {
  color: rgba(255, 255, 255, 0.55) !important;
}

/* 空状态 */
.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--fintech-space-12);
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--fintech-gray-6);
  margin-bottom: var(--fintech-space-4);
  opacity: 0.5;
}

.empty-content h4 {
  margin: 0 0 var(--fintech-space-2) 0;
  font-size: var(--fintech-font-size-xl);
  font-weight: 500;
}

.empty-content p {
  margin: 0 0 var(--fintech-space-6) 0;
  font-size: var(--fintech-font-size-base);
}

/* 表格底部 */
.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fintech-space-4) var(--fintech-space-5);
  border-top: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-tertiary);
}

.pagination-info {
  font-size: var(--fintech-font-size-sm);
  font-family: var(--fintech-font-family-data);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--fintech-space-2);
}

.pagination-btn,
.page-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--fintech-border-base);
  background: var(--fintech-bg-secondary);
  color: var(--fintech-text-primary);
  cursor: pointer;
  border-radius: var(--fintech-radius-sm);
  transition: all var(--fintech-transition-fast);
  font-size: var(--fintech-font-size-sm);
  font-family: var(--fintech-font-family-data);
}

.pagination-btn:hover:not(:disabled),
.page-number:hover:not(.active) {
  background: var(--fintech-bg-elevated);
  border-color: var(--fintech-border-light);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number.active {
  background: var(--fintech-accent-primary);
  border-color: var(--fintech-accent-primary);
  color: white;
  font-weight: 600;
}

/* 加载状态 */
.table-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(10, 14, 39, 0.9);
  backdrop-filter: blur(4px);
  z-index: 20;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--fintech-border-base);
  border-top: 3px solid var(--fintech-accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--fintech-space-4);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: var(--fintech-font-size-base);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: var(--fintech-space-3);
    align-items: flex-start;
  }

  .table-footer {
    flex-direction: column;
    gap: var(--fintech-space-3);
    align-items: stretch;
  }

  .pagination-controls {
    justify-content: center;
  }

  .data-table {
    font-size: var(--fintech-font-size-xs);
  }

  .data-table th,
  .data-table td {
    padding: var(--fintech-space-2);
  }
}

@media (max-width: 480px) {
  .data-table th .header-content {
    flex-direction: column;
    gap: var(--fintech-space-1);
  }

  .sort-icon {
    font-size: 10px;
  }

  .pagination-btn,
  .page-number {
    width: 28px;
    height: 28px;
    font-size: var(--fintech-font-size-xs);
  }
}

/* 高分辨率优化 */
@media (min-width: 1920px) {
  .data-table th,
  .data-table td {
    padding: var(--fintech-space-4);
  }

  .table-container {
    max-height: 800px;
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .data-table th {
    background: var(--fintech-bg-tertiary);
  }

  .data-table td {
    border-color: var(--fintech-border-dark);
  }
}
</style>