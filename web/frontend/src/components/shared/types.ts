// Shared component types
// Extracted from Vue components for proper TypeScript support

// FilterBar types
export interface FilterOption {
  label: string
  value: string | number | boolean
}

export interface FilterItem {
  key: string
  label: string
  type: 'input' | 'select' | 'date-picker' | 'date-range' | 'cascader' | 'input-number'
  placeholder?: string
  width?: string
  options?: FilterOption[]
  defaultValue?: unknown
}

// StockListTable types
export interface TableColumn<T = unknown> {
  prop?: string
  label: string
  width?: string | number
  minWidth?: string | number
  align?: 'left' | 'center' | 'right'
  sortable?: boolean | 'custom'
  formatter?: (row: T, column: TableColumn, cellValue: unknown, index: number) => string
  slotName?: string
  className?: string
  colorClass?: string | ((row: T) => string)
}

export interface TableAction {
  label: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  icon?: string
  disabled?: (row: unknown) => boolean
  show?: (row: unknown) => boolean
}

export interface TableActionItem {
  action: string
  label: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  icon?: string
  disabled?: (row: unknown) => boolean
  visible?: (row: unknown) => boolean
}

// CommandPalette types
export interface CommandItem {
  id: string
  label: string
  description?: string
  icon?: string
  category?: string
  action?: () => void
  children?: CommandItem[]
}
