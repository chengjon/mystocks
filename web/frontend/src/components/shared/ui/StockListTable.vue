<template>
  <div class="stock-list-table">
    <el-table
      :data="data"
      :loading="loading"
      :height="height"
      :max-height="maxHeight"
      :stripe="stripe"
      :border="border"
      :show-header="showHeader"
      :empty-text="emptyText"
      class="artdeco-table"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
    >
      <!-- Selection Column -->
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        :selectable="selectableFunction"
      />

      <!-- Index Column -->
      <el-table-column
        v-if="showIndex"
        type="index"
        label="#"
        width="60"
        align="center"
        :index="indexMethod"
      />

      <!-- Dynamic Columns -->
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :fixed="column.fixed"
        :sortable="column.sortable ? 'custom' : false"
        :align="column.align || 'left'"
        :class-name="column.className"
      >
        <template #default="{ row, column: col, $index }">
          <!-- Custom slot for column -->
          <slot
            v-if="$slots[`column-${column.prop}`]"
            :name="`column-${column.prop}`"
            :row="row"
            :column="col"
            :index="$index"
          />
          <!-- Default rendering -->
          <span v-else :class="getCellClass(row, column)">
            {{ formatCellValue(row[column.prop], column) }}
          </span>
        </template>
      </el-table-column>

      <!-- Action Column -->
      <el-table-column
        v-if="showActions"
        label="Actions"
        :width="actionWidth"
        :fixed="actionsFixed"
        align="center"
      >
        <template #default="{ row, $index }">
          <div class="table-actions">
            <template v-for="action in actions" :key="action.key">
              <!-- Button Action -->
              <el-button
                v-if="action.type === 'button'"
                :type="action.variant || 'default'"
                :size="action.size || 'small'"
                :icon="action.icon"
                :disabled="action.disabled?.(row) || false"
                :loading="action.loading?.(row) || false"
                @click.stop="handleAction(action, row, $index)"
              >
                {{ action.text }}
              </el-button>

              <!-- Icon Button Action -->
              <el-tooltip
                v-else-if="action.type === 'icon'"
                :content="action.text"
                placement="top"
              >
                <el-button
                  :type="action.variant || 'default'"
                  :size="action.size || 'small'"
                  :icon="action.icon"
                  :disabled="action.disabled?.(row) || false"
                  :loading="action.loading?.(row) || false"
                  circle
                  @click.stop="handleAction(action, row, $index)"
                />
              </el-tooltip>

              <!-- Dropdown Action -->
              <el-dropdown
                v-else-if="action.type === 'dropdown'"
                trigger="click"
                @command="(cmd) => handleDropdownCommand(cmd, action, row, $index)"
              >
                <el-button :size="action.size || 'small'">
                  {{ action.text }}
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-for="item in action.items"
                      :key="item.key"
                      :command="item.key"
                      :icon="item.icon"
                      :disabled="item.disabled?.(row) || false"
                    >
                      {{ item.text }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </div>
        </template>
      </el-table-column>

      <!-- Empty Slot -->
      <template #empty>
        <div class="table-empty">
          <el-icon><DocumentDelete /></el-icon>
          <p>{{ emptyText }}</p>
        </div>
      </template>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowDown, DocumentDelete } from '@element-plus/icons-vue'
import type { TableColumnCtx } from 'element-plus'

export interface TableColumn {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  fixed?: boolean | 'left' | 'right'
  sortable?: boolean
  align?: 'left' | 'center' | 'right'
  className?: string
  formatter?: (value: any, row: any) => string
  colorClass?: (value: any, row: any) => string
}

export interface TableAction {
  key: string
  text: string
  type: 'button' | 'icon' | 'dropdown'
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  size?: 'large' | 'default' | 'small'
  icon?: any
  disabled?: (row: any) => boolean
  loading?: (row: any) => boolean
  handler?: (row: any, index: number) => void
  items?: TableActionItem[]
}

export interface TableActionItem {
  key: string
  text: string
  icon?: any
  disabled?: (row: any) => boolean
  handler?: (row: any, index: number) => void
}

interface Props {
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  height?: string | number
  maxHeight?: string | number
  stripe?: boolean
  border?: boolean
  showHeader?: boolean
  showIndex?: boolean
  indexMethod?: (index: number) => number
  selectable?: boolean
  selectableFunction?: (row: any, index: number) => boolean
  showActions?: boolean
  actions?: TableAction[]
  actionWidth?: number
  actionsFixed?: boolean | 'left' | 'right'
  emptyText?: string
  rowClickable?: boolean
}

interface Emits {
  (e: 'selection-change', selection: any[]): void
  (e: 'sort-change', sort: { column: any; prop: string; order: string | null }): void
  (e: 'row-click', row: any, column: any, index: number): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  stripe: true,
  border: false,
  showHeader: true,
  showIndex: false,
  selectable: false,
  selectableFunction: () => true,
  showActions: true,
  actions: () => [],
  actionWidth: 200,
  actionsFixed: 'right',
  emptyText: 'No Data Available',
  rowClickable: false
})

const emit = defineEmits<Emits>()

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

const handleSortChange = (sort: { column: any; prop: string; order: string | null }) => {
  emit('sort-change', sort)
}

const handleRowClick = (row: any, column: any, index: number) => {
  if (props.rowClickable) {
    emit('row-click', row, column, index)
  }
}

const handleAction = (action: TableAction, row: any, index: number) => {
  if (action.handler) {
    action.handler(row, index)
  }
}

const handleDropdownCommand = (
  command: string,
  action: TableAction,
  row: any,
  index: number
) => {
  const item = action.items?.find(i => i.key === command)
  if (item && item.handler) {
    item.handler(row, index)
  }
}

const formatCellValue = (value: any, column: TableColumn) => {
  if (column.formatter) {
    return column.formatter(value, {})
  }
  return value
}

const getCellClass = (row: any, column: TableColumn) => {
  if (column.colorClass) {
    return column.colorClass(row[column.prop], row)
  }
  return ''
}
</script>

<style scoped lang="scss">

.stock-list-table {
  width: 100%;

  .artdeco-table {
    background: var(--artdeco-bg-secondary);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: var(--artdeco-radius-sm);

    :deep(.el-table__header-wrapper) {
      background: rgba(212, 175, 55, 0.05);

      th {
        background: transparent;
        border-bottom: 2px solid var(--artdeco-accent-gold);

        .cell {
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-font-size-xs);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--artdeco-tracking-wider);
          color: var(--artdeco-accent-gold);
        }

        .caret-wrapper {
          .sort-caret {
            border-color: rgba(212, 175, 55, 0.5);

            &.ascending {
              bottom: -2px;
              border-top-color: var(--artdeco-accent-gold);
            }

            &.descending {
              top: -2px;
              border-bottom-color: var(--artdeco-accent-gold);
            }
          }
        }
      }
    }

    :deep(.el-table__body-wrapper) {
      .el-table__row {
        background: transparent;
        transition: all var(--artdeco-transition-base);
        cursor: pointer;

        &:hover {
          background: rgba(212, 175, 55, 0.05);
        }

        &.el-table__row--striped {
          background: rgba(0, 0, 0, 0.2);

          &:hover {
            background: rgba(212, 175, 55, 0.05);
          }
        }

        td {
          border-bottom: 1px solid rgba(212, 175, 55, 0.1);

          .cell {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-font-size-small);
            color: var(--artdeco-fg-primary);
          }
        }
      }
    }

    :deep(.el-table__empty-block) {
      background: transparent;
      border: none;
    }

    .table-empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: var(--artdeco-spacing-3);
      padding: var(--artdeco-spacing-8);
      color: var(--artdeco-fg-muted);

      .el-icon {
        font-size: 48px;
        opacity: 0.5;
      }

      p {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-body);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        margin: 0;
      }
    }

    .table-actions {
      display: flex;
      gap: var(--artdeco-spacing-2);
      justify-content: center;
      align-items: center;

      .el-button {
        font-family: var(--artdeco-font-display);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wider);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: var(--artdeco-radius-none);
        transition: all var(--artdeco-transition-base);

        &.el-button--primary {
          background: var(--artdeco-accent-gold);
          border-color: var(--artdeco-accent-gold);
          color: var(--artdeco-bg-primary);

          &:hover {
            background: var(--artdeco-accent-gold-light);
            border-color: var(--artdeco-accent-gold-light);
          }
        }

        &.el-button--success {
          background: var(--artdeco-color-up);
          border-color: var(--artdeco-color-up);
          color: var(--artdeco-bg-primary);

          &:hover {
            background: #27AE60;
            border-color: #27AE60;
          }
        }

        &.el-button--danger {
          background: var(--artdeco-color-down);
          border-color: var(--artdeco-color-down);
          color: var(--artdeco-bg-primary);

          &:hover {
            background: #C0392B;
            border-color: #C0392B;
          }
        }

        &:not(.el-button--primary):not(.el-button--success):not(.el-button--danger) {
          background: transparent;
          border-color: rgba(212, 175, 55, 0.3);
          color: var(--artdeco-accent-gold);

          &:hover {
            background: rgba(212, 175, 55, 0.05);
            border-color: var(--artdeco-accent-gold);
          }
        }

        &:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }
      }

      .el-tooltip {
        .el-button {
          padding: 5px;

          &.is-circle {
            width: 28px;
            height: 28px;
          }
        }
      }
    }

    /* Color utility classes */
    .color-up {
      color: var(--artdeco-color-up);
      font-weight: 600;
    }

    .color-down {
      color: var(--artdeco-color-down);
      font-weight: 600;
    }

    .color-neutral {
      color: var(--artdeco-fg-muted);
    }
  }
}

@media (max-width: 768px) {
  .stock-list-table {
    .artdeco-table {
      :deep(.el-table__header-wrapper) {
        th .cell {
          font-size: var(--artdeco-font-size-xs);
          padding: 0 4px;
        }
      }

      :deep(.el-table__body-wrapper) {
        td .cell {
          font-size: 11px;
          padding: 0 4px;
        }
      }

      .table-actions {
        flex-direction: column;
        gap: var(--artdeco-spacing-1);

        .el-button {
          width: 100%;
          font-size: 11px;
          padding: 4px 8px;
        }
      }
    }
  }
}
</style>
