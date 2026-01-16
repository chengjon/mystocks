<template>
    <div class="artdeco-filter-bar">
        <div class="filter-bar-header">
            <h4 class="filter-title">{{ title || 'FILTERS' }}</h4>
            <div class="header-actions">
                <button v-if="showReset" class="reset-btn" @click="handleReset">RESET</button>
                <button v-if="showClear" class="clear-btn" @click="handleClear">CLEAR</button>
                <button v-if="showToggle" class="toggle-btn" @click="handleToggle">
                    {{ expanded ? '▼' : '▲' }}
                </button>
            </div>
        </div>

        <div v-if="expanded" class="filter-bar-body">
            <div class="filters-grid">
                <div v-for="filter in filters" :key="filter.key" class="filter-item">
                    <label class="filter-label">{{ filter.label }}</label>

                    <div v-if="filter.type === 'text'" class="filter-input-wrapper">
                        <input
                            v-model="filterValues[filter.key]"
                            type="text"
                            :placeholder="filter.placeholder || `Search ${filter.label}`"
                            class="artdeco-input"
                            @input="handleFilterChange(filter.key)"
                        />
                    </div>

                    <div v-else-if="filter.type === 'select'" class="filter-input-wrapper">
                        <ArtDecoSelect
                            v-model="filterValues[filter.key]"
                            :placeholder="filter.placeholder || `Select ${filter.label}`"
                            :options="filter.options || []"
                            :clearable="filter.clearable !== false"
                            @update:modelValue="handleFilterChange(filter.key)"
                        />
                    </div>

                    <div v-else-if="filter.type === 'multi-select'" class="filter-input-wrapper">
                        <el-select
                            v-model="filterValues[filter.key]"
                            :placeholder="filter.placeholder || `Select ${filter.label}`"
                            :multiple="true"
                            :collapse-tags="true"
                            :clearable="filter.clearable !== false"
                            class="artdeco-multi-select"
                            @change="handleFilterChange(filter.key)"
                        >
                            <el-option
                                v-for="option in filter.options"
                                :key="option.value"
                                :label="option.label"
                                :value="option.value"
                            />
                        </el-select>
                    </div>

                    <div v-else-if="filter.type === 'date-range'" class="filter-input-wrapper">
                        <el-date-picker
                            v-model="filterValues[filter.key]"
                            type="daterange"
                            :range-separator="filter.rangeSeparator || 'TO'"
                            :start-placeholder="filter.startPlaceholder || 'Start'"
                            :end-placeholder="filter.endPlaceholder || 'End'"
                            :format="filter.dateFormat || 'YYYY-MM-DD'"
                            :value-format="filter.valueFormat || 'YYYY-MM-DD'"
                            class="artdeco-date-picker"
                            @change="handleFilterChange(filter.key)"
                        />
                    </div>

                    <div v-else-if="filter.type === 'number'" class="filter-input-wrapper">
                        <div class="number-range">
                            <input
                                v-model.number="filterValues[`${filter.key}_min`]"
                                type="number"
                                :placeholder="filter.minPlaceholder || 'Min'"
                                class="artdeco-input number-input"
                                @input="handleFilterChange(filter.key)"
                            />
                            <span class="range-separator">-</span>
                            <input
                                v-model.number="filterValues[`${filter.key}_max`]"
                                type="number"
                                :placeholder="filter.maxPlaceholder || 'Max'"
                                class="artdeco-input number-input"
                                @input="handleFilterChange(filter.key)"
                            />
                        </div>
                    </div>

                    <div v-else-if="filter.type === 'checkbox-group'" class="filter-input-wrapper">
                        <div class="checkbox-group">
                            <label v-for="option in filter.options" :key="option.value" class="checkbox-label">
                                <input
                                    v-model="filterValues[filter.key]"
                                    type="checkbox"
                                    :value="option.value"
                                    @change="handleFilterChange(filter.key)"
                                />
                                <span>{{ option.label }}</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="showQuickFilters && quickFilters.length > 0" class="quick-filters">
                <span class="quick-filters-label">QUICK:</span>
                <button
                    v-for="quick in quickFilters"
                    :key="quick.key"
                    class="quick-filter-btn"
                    :class="{ active: activeQuickFilter === quick.key }"
                    @click="handleQuickFilter(quick)"
                >
                    {{ quick.label }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, computed } from 'vue'
    import ArtDecoSelect from '../base/ArtDecoSelect.vue'

    interface FilterOption {
        label: string
        value: any
    }

    interface Filter {
        key: string
        label: string
        type: 'text' | 'select' | 'multi-select' | 'date-range' | 'number' | 'checkbox-group'
        placeholder?: string
        clearable?: boolean
        options?: FilterOption[]
        rangeSeparator?: string
        startPlaceholder?: string
        endPlaceholder?: string
        dateFormat?: string
        valueFormat?: string
        minPlaceholder?: string
        maxPlaceholder?: string
    }

    interface QuickFilter {
        key: string
        label: string
        filters: Record<string, any>
    }

    interface Props {
        title?: string
        filters: Filter[]
        quickFilters?: QuickFilter[]
        showReset?: boolean
        showClear?: boolean
        showToggle?: boolean
        showQuickFilters?: boolean
        defaultExpanded?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        quickFilters: () => [],
        showReset: true,
        showClear: true,
        showToggle: true,
        showQuickFilters: true,
        defaultExpanded: true
    })

    const emit = defineEmits<{
        filterChange: [filters: Record<string, any>]
        reset: []
        clear: []
    }>()

    const expanded = ref(props.defaultExpanded)
    const activeQuickFilter = ref<string>('')

    const filterValues = reactive<Record<string, any>>(() => {
        const values: Record<string, any> = {}
        props.filters.forEach(filter => {
            if (filter.type === 'number') {
                values[`${filter.key}_min`] = null
                values[`${filter.key}_max`] = null
            } else if (filter.type === 'multi-select' || filter.type === 'checkbox-group') {
                values[filter.key] = []
            } else {
                values[filter.key] = null
            }
        })
        return values
    })

    const activeFiltersCount = computed(() => {
        let count = 0
        Object.values(filterValues).forEach(value => {
            if (value !== null && value !== '' && (Array.isArray(value) ? value.length > 0 : true)) {
                count++
            }
        })
        return count
    })

    const handleFilterChange = (key: string) => {
        activeQuickFilter.value = ''
        emit('filterChange', filterValues)
    }

    const handleQuickFilter = (quick: QuickFilter) => {
        if (activeQuickFilter.value === quick.key) {
            activeQuickFilter.value = ''
            Object.keys(filterValues).forEach(k => {
                if (Array.isArray(filterValues[k])) {
                    filterValues[k] = []
                } else {
                    filterValues[k] = null
                }
            })
        } else {
            activeQuickFilter.value = quick.key
            Object.assign(filterValues, quick.filters)
        }
        emit('filterChange', filterValues)
    }

    const handleReset = () => {
        props.filters.forEach(filter => {
            if (filter.type === 'number') {
                filterValues[`${filter.key}_min`] = null
                filterValues[`${filter.key}_max`] = null
            } else if (filter.type === 'multi-select' || filter.type === 'checkbox-group') {
                filterValues[filter.key] = []
            } else {
                filterValues[filter.key] = null
            }
        })
        activeQuickFilter.value = ''
        emit('reset')
        emit('filterChange', filterValues)
    }

    const handleClear = () => {
        activeQuickFilter.value = ''
        emit('clear')
    }

    const handleToggle = () => {
        expanded.value = !expanded.value
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-filter-bar {
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--artdeco-spacing-4);
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-4);
    }

    /* Filter bar header */
    .filter-bar-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .filter-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      margin: 0;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
    }

    .reset-btn,
    .clear-btn,
    .toggle-btn {
      background: transparent;
      border: none;
      color: var(--artdeco-fg-muted);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      transition: all var(--artdeco-transition-base);
    }

    .reset-btn:hover,
    .clear-btn:hover,
    .toggle-btn:hover {
      color: var(--artdeco-accent-gold);
    }

    /* Filter bar body */
    .filter-bar-body {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-4);
    }

    .filters-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: var(--artdeco-spacing-3);
    }

    .filter-item {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);
    }

    .filter-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .filter-input-wrapper {
      width: 100%;
    }

    .artdeco-input {
      width: 100%;
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-input:focus {
      outline: none;
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-multi-select,
    .artdeco-date-picker {
      width: 100%;
    }

    .number-range {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
    }

    .number-input {
      flex: 1;
    }

    .range-separator {
      color: var(--artdeco-fg-muted);
    }

    .checkbox-group {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      color: var(--artdeco-fg-secondary);
      cursor: pointer;
    }

    .checkbox-label input[type="checkbox"] {
      accent-color: var(--artdeco-accent-gold);
    }

    /* Quick filters */
    .quick-filters {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .quick-filters-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .quick-filter-btn {
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
    }

    .quick-filter-btn:hover {
      border-color: var(--artdeco-accent-gold);
      color: var(--artdeco-accent-gold);
    }

    .quick-filter-btn.active {
      background: var(--artdeco-accent-gold);
      border-color: var(--artdeco-accent-gold);
      color: var(--artdeco-bg-primary);
    }
</style>
