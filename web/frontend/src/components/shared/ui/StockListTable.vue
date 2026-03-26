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
      class="table"
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
        v-for="(column, _idx) in columns"
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
                :icon="action.icon as string | undefined"
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
                  :icon="action.icon as string | undefined"
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
                      v-for="(item, _idx) in action.items"
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
import { ArrowDown, DocumentDelete } from '@element-plus/icons-vue'

export interface TableColumn {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  fixed?: boolean | 'left' | 'right'
  sortable?: boolean
  align?: 'left' | 'center' | 'right'
  className?: string
  formatter?: (value: unknown, row: unknown) => string
  colorClass?: (value: unknown, row: unknown) => string
}

export interface TableAction {
  key: string
  text: string
  type: 'button' | 'icon' | 'dropdown'
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  size?: 'large' | 'default' | 'small'
  icon?: string | object
  disabled?: (row: unknown) => boolean
  loading?: (row: unknown) => boolean
  handler?: (row: unknown, index: number) => void
  items?: TableActionItem[]
}

export interface TableActionItem {
  key: string
  text: string
  icon?: string | object
  disabled?: (row: unknown) => boolean
  handler?: (row: unknown, index: number) => void
}

interface Props {
  data: unknown[]
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
  selectableFunction?: (row: unknown, index: number) => boolean
  showActions?: boolean
  actions?: TableAction[]
  actionWidth?: number
  actionsFixed?: boolean | 'left' | 'right'
  emptyText?: string
  rowClickable?: boolean
}

interface Emits {
  (e: 'selection-change', selection: unknown[]): void
  (e: 'sort-change', sort: { column: unknown; prop: string; order: string | null }): void
  (e: 'row-click', row: unknown, column: unknown, index: number): void
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

const handleSelectionChange = (selection: unknown[]) => {
  emit('selection-change', selection)
}

const handleSortChange = (sort: { column: unknown; prop: string; order: string | null }) => {
  emit('sort-change', sort)
}

const handleRowClick = (row: unknown, column: unknown, index: number) => {
  if (props.rowClickable) {
    emit('row-click', row, column, index)
  }
}

const handleAction = (action: TableAction, row: unknown, index: number) => {
  if (action.handler) {
    action.handler(row, index)
  }
}

const handleDropdownCommand = (
  command: string,
  action: TableAction,
  row: unknown,
  index: number
) => {
  const item = action.items?.find(i => i.key === command)
  if (item && item.handler) {
    item.handler(row, index)
  }
}

const formatCellValue = (value: unknown, column: TableColumn) => {
  if (column.formatter) {
    return column.formatter(value, {})
  }
  return value
}

const getCellClass = (row: Record<string, unknown>, column: TableColumn) => {
  if (column.colorClass) {
    return column.colorClass(row[column.prop], row)
  }
  return ''
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';
.stock-list-table {
  width: 100%;
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-opacity-20);
  border-radius: var(--artdeco-radius-sm);

  :deep(.el-table__header-wrapper) {
    background: var(--artdeco-gold-opacity-05);

    th {
      background: transparent;
      border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);

      .cell {
        font-family: var(--font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        color: var(--artdeco-gold-primary);
      }

      .caret-wrapper {
        .sort-caret {
          border-color: var(--artdeco-gold-opacity-shadow);

          &.ascending {
            bottom: calc(var(--artdeco-spacing-px) * -2);
            border-top-color: var(--artdeco-gold-primary);
          }

          &.descending {
            top: calc(var(--artdeco-spacing-px) * -2);
            border-bottom-color: var(--artdeco-gold-primary);
          }
        }
      }
    }
  }

  :deep(.el-table__body-wrapper) {
    .el-table__row {
      background: transparent;
      transition: all 0.3s;
      cursor: pointer;

      &:hover {
        background: var(--artdeco-gold-opacity-05);
      }

      &.el-table__row--striped {
        background: color-mix(in srgb, var(--artdeco-bg-global) 20%, transparent);

        &:hover {
          background: var(--artdeco-gold-opacity-05);
        }
      }

      td {
        border-bottom: 1px solid var(--artdeco-gold-opacity-10);

        .cell {
          font-family: var(--font-body);
          font-size: var(--artdeco-text-sm);
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
      font-size: var(--artdeco-text-5xl);
      opacity: 50%;
    }

    p {
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: calc(var(--artdeco-spacing-px) / 2);
      margin: 0;
    }
  }

  .table-actions {
    display: flex;
    gap: var(--artdeco-spacing-2);
    justify-content: center;
    align-items: center;

    .el-button {
      font-family: var(--font-body);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      border: 1px solid var(--artdeco-border-default);
      border-radius: var(--artdeco-radius-none);
      transition: all 0.3s;

      &.el-button--primary {
        background: var(--artdeco-gold-primary);
        border-color: var(--artdeco-gold-primary);
        color: var(--artdeco-bg-global);

        &:hover {
          background: var(--artdeco-gold-light);
          border-color: var(--artdeco-gold-light);
        }
      }

      &.el-button--success {
        background: var(--artdeco-success);
        border-color: var(--artdeco-success);
        color: var(--artdeco-bg-global);

        &:hover {
          background: color-mix(in srgb, var(--artdeco-success) 85%, var(--artdeco-bg-global));
          border-color: color-mix(in srgb, var(--artdeco-success) 85%, var(--artdeco-bg-global));
        }
      }

      &.el-button--danger {
        background: var(--artdeco-error);
        border-color: var(--artdeco-error);
        color: var(--artdeco-bg-global);

        &:hover {
          background: color-mix(in srgb, var(--artdeco-error) 85%, var(--artdeco-bg-global));
          border-color: color-mix(in srgb, var(--artdeco-error) 85%, var(--artdeco-bg-global));
        }
      }

      &:not(.el-button--primary, .el-button--success, .el-button--danger) {
        background: transparent;
        border-color: var(--artdeco-border-default);
        color: var(--artdeco-gold-primary);

        &:hover {
          background: var(--artdeco-gold-opacity-05);
          border-color: var(--artdeco-gold-primary);
        }
      }

      &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
      }
    }

    .el-tooltip {
      .el-button {
        padding: calc(var(--artdeco-spacing-px) * 5);

        &.is-circle {
          width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
          height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
        }
      }
    }
  }

  /* Color utility classes */
  .color-up {
    color: var(--artdeco-success);
    font-weight: 600;
  }

  .color-down {
    color: var(--artdeco-error);
    font-weight: 600;
  }

  .color-neutral {
    color: var(--artdeco-fg-muted);
  }
}

@media (width <= var(--artdeco-breakpoint-md)) {
  .stock-list-table {
    :deep(.el-table__header-wrapper) {
      th .cell {
        font-size: var(--artdeco-text-xs);
        padding: 0 var(--artdeco-spacing-1);
      }
    }

    :deep(.el-table__body-wrapper) {
      td .cell {
        font-size: var(--artdeco-text-xs);
        padding: 0 var(--artdeco-spacing-1);
      }
    }

    .table-actions {
      flex-direction: column;
      gap: var(--artdeco-spacing-1);

      .el-button {
        width: 100%;
        font-size: var(--artdeco-text-xs);
        padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      }
    }
  }
}
</style>
