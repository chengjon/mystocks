<template>
  <div class="filter-bar">
    <el-form :inline="true" :model="formData" class="filter-form">
      <el-form-item
        v-for="filter in filters"
        :key="filter.key"
        :label="filter.label"
      >
        <!-- 输入框 -->
        <el-input
          v-if="filter.type === 'input'"
          v-model="formData[filter.key]"
          :placeholder="filter.placeholder || `Search ${filter.label}`"
          clearable
          :style="{ width: filter.width || '150px' }"
          @keyup.enter="handleSearch"
        />

        <!-- 下拉选择 -->
        <el-select
          v-else-if="filter.type === 'select'"
          v-model="formData[filter.key]"
          :placeholder="filter.placeholder || 'All'"
          clearable
          :style="{ width: filter.width || '120px' }"
        >
          <el-option
            v-for="option in filter.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <!-- 日期选择器 -->
        <el-date-picker
          v-else-if="filter.type === 'date-picker'"
          v-model="formData[filter.key]"
          type="date"
          :placeholder="filter.placeholder || 'Select date'"
          :style="{ width: filter.width || '150px' }"
        />

        <!-- 日期范围选择器 -->
        <el-date-picker
          v-else-if="filter.type === 'date-range'"
          v-model="formData[filter.key]"
          type="daterange"
          range-separator="TO"
          start-placeholder="START DATE"
          end-placeholder="END DATE"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :style="{ width: filter.width || '260px' }"
        />
      </el-form-item>

      <el-form-item>
        <div class="filter-actions">
          <el-button
            type="primary"
            @click="handleSearch"
            :loading="loading"
          >
            <template #icon>
              <el-icon><Search /></el-icon>
            </template>
            Search
          </el-button>
          <el-button
            @click="handleReset"
          >
            <template #icon>
              <el-icon><RefreshLeft /></el-icon>
            </template>
            Reset
          </el-button>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Search, RefreshLeft } from '@element-plus/icons-vue'

export interface FilterOption {
  label: string
  value: any
}

export interface FilterItem {
  key: string
  label: string
  type: 'input' | 'select' | 'date-picker' | 'date-range'
  placeholder?: string
  width?: string
  options?: FilterOption[]
  defaultValue?: any
}

interface Props {
  filters: FilterItem[]
  loading?: boolean
  modelValue?: Record<string, any>
}

interface Emits {
  (e: 'search', params: Record<string, any>): void
  (e: 'reset'): void
  (e: 'update:modelValue', value: Record<string, any>): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  modelValue: undefined
})

const emit = defineEmits<Emits>()

const formData = reactive<Record<string, any>>({})

// Initialize form data with defaults
props.filters.forEach(filter => {
  formData[filter.key] = filter.defaultValue !== undefined ? filter.defaultValue : ''
})

// Watch for external model changes
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    Object.assign(formData, newVal)
  }
}, { immediate: true, deep: true })

// Emit changes to parent
watch(formData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

const handleSearch = () => {
  const params = { ...formData }

  // Remove empty values
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === null || params[key] === undefined) {
      delete params[key]
    }
  })

  emit('search', params)
}

const handleReset = () => {
  props.filters.forEach(filter => {
    formData[filter.key] = filter.defaultValue !== undefined ? filter.defaultValue : ''
  })
  emit('reset')
}

defineExpose({
  reset: handleReset,
  getFormData: () => ({ ...formData }),
  setFieldValue: (key: string, value: any) => {
    formData[key] = value
  }
})
</script>

<style scoped lang="scss">
// Phase 3.4: Design Token Migration
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

.filter-bar {
  margin-bottom: var(--spacing-xl);

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    align-items: flex-end;

    :deep(.el-form-item) {
      margin-bottom: 0;
    }

    :deep(.el-form-item__label) {
      font-family: var(--font-family-sans);
      font-size: var(--font-size-xs);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--color-accent);
    }
  }

  .filter-actions {
    display: flex;
    gap: var(--spacing-sm);

    .el-button {
      font-family: var(--font-family-sans);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border: 2px solid var(--color-accent);
      border-radius: 0;

      &.el-button--primary {
        background: var(--color-accent);
        border-color: var(--color-accent);
        color: var(--color-bg-primary);

        &:hover {
          background: var(--color-accent-hover);
          border-color: var(--color-accent-hover);
        }
      }

      &:not(.el-button--primary) {
        background: transparent;
        border-color: var(--color-accent-alpha-70);
        color: var(--color-accent);

        &:hover {
          background: var(--color-accent-alpha-90);
          border-color: var(--color-accent);
        }
      }
    }
  }
}

// ============================================
//   DESIGN NOTE - 设计说明
//   本项目仅支持桌面端，不包含移动端响应式代码
// ============================================
</style>
