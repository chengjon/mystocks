<template>
  <div class="indicator-selector">
    <el-popover
      :width="400"
      trigger="click"
      placement="bottom-start"
    >
      <template #reference>
        <el-button
          size="small"
          :icon="TrendCharts"
        >
          技术指标
          <el-badge
            v-if="selectedCount > 0"
            :value="selectedCount"
            class="indicator-badge"
          />
        </el-button>
      </template>

      <div class="indicator-panel">
        <!-- 分类标签 -->
        <el-tabs v-model="activeCategory" class="indicator-tabs">
          <!-- 趋势指标 -->
          <el-tab-pane label="趋势" name="trend">
            <div class="indicator-list">
              <!-- @ts-expect-error Element Plus CheckboxValueType type limitation -->
              <el-checkbox
                v-for="(indicator, idx) in trendIndicators"
                :key="idx"
                :model-value="isIndicatorSelected(indicator.value)"
                @change="onCheckboxChange(indicator.value, $event)"
              >
                <div class="indicator-item">
                  <span class="indicator-name">{{ indicator.label }}</span>
                  <span class="indicator-desc">{{ indicator.description }}</span>
                </div>
              </el-checkbox>
            </div>
          </el-tab-pane>

          <!-- 动量指标 -->
          <el-tab-pane label="动量" name="momentum">
            <div class="indicator-list">
              <!-- @ts-expect-error Element Plus CheckboxValueType type limitation -->
              <el-checkbox
                v-for="(indicator, idx) in momentumIndicators"
                :key="idx"
                :model-value="isIndicatorSelected(indicator.value)"
                @change="onCheckboxChange(indicator.value, $event)"
              >
                <div class="indicator-item">
                  <span class="indicator-name">{{ indicator.label }}</span>
                  <span class="indicator-desc">{{ indicator.description }}</span>
                </div>
              </el-checkbox>
            </div>
          </el-tab-pane>

          <!-- 波动率指标 -->
          <el-tab-pane label="波动率" name="volatility">
            <div class="indicator-list">
              <!-- @ts-expect-error Element Plus CheckboxValueType type limitation -->
              <el-checkbox
                v-for="(indicator, idx) in volatilityIndicators"
                :key="idx"
                :model-value="isIndicatorSelected(indicator.value)"
                @change="onCheckboxChange(indicator.value, $event)"
              >
                <div class="indicator-item">
                  <span class="indicator-name">{{ indicator.label }}</span>
                  <span class="indicator-desc">{{ indicator.description }}</span>
                </div>
              </el-checkbox>
            </div>
          </el-tab-pane>

          <!-- 成交量指标 -->
          <el-tab-pane label="成交量" name="volume">
            <div class="indicator-list">
              <!-- @ts-expect-error Element Plus CheckboxValueType type limitation -->
              <el-checkbox
                v-for="(indicator, idx) in volumeIndicators"
                :key="idx"
                :model-value="isIndicatorSelected(indicator.value)"
                @change="onCheckboxChange(indicator.value, $event)"
              >
                <div class="indicator-item">
                  <span class="indicator-name">{{ indicator.label }}</span>
                  <span class="indicator-desc">{{ indicator.description }}</span>
                </div>
              </el-checkbox>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 快捷操作 -->
        <div class="indicator-actions">
          <el-button
            size="small"
            @click="handleClearAll"
          >
            清空
          </el-button>
          <el-button
            size="small"
            type="primary"
            @click="handleApply"
          >
            应用 ({{ selectedCount }})
          </el-button>
        </div>
      </div>
    </el-popover>

    <!-- 已选指标标签 -->
    <div v-if="showSelectedTags && selectedIndicators.length > 0" class="selected-tags">
      <el-tag
        v-for="indicator in selectedIndicators"
        :key="indicator"
        closable
        size="small"
        @close="handleRemoveIndicator(indicator)"
      >
        {{ getIndicatorLabel(indicator) }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'
import type { CheckboxValueType } from 'element-plus'
import type { IndicatorMeta } from '@/types/indicators'

/**
 * 组件Props
 */
interface IndicatorSelectorProps {
  /** 当前选中的指标列表 */
  modelValue?: string[]
  /** 是否显示已选标签 */
  showSelectedTags?: boolean
}

// Props with defaults
const props = withDefaults(defineProps<IndicatorSelectorProps>(), {
  modelValue: () => [],
  showSelectedTags: true
})

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', indicators: string[]): void
  (e: 'change', indicators: string[]): void
}>()

// Refs
const selectedIndicators = ref<string[]>([...props.modelValue])
const activeCategory = ref<'trend' | 'momentum' | 'volatility' | 'volume'>('trend')

// 趋势指标
const trendIndicators: IndicatorMeta[] = [
  { label: 'MA5', value: 'MA5', description: '5日移动平均线', category: 'trend', params: [5] },
  { label: 'MA10', value: 'MA10', description: '10日移动平均线', category: 'trend', params: [10] },
  { label: 'MA20', value: 'MA20', description: '20日移动平均线', category: 'trend', params: [20] },
  { label: 'MA60', value: 'MA60', description: '60日移动平均线', category: 'trend', params: [60] },
  { label: 'EMA12', value: 'EMA12', description: '12日指数移动平均', category: 'trend', params: [12] },
  { label: 'EMA26', value: 'EMA26', description: '26日指数移动平均', category: 'trend', params: [26] }
]

// 动量指标
const momentumIndicators: IndicatorMeta[] = [
  { label: 'MACD', value: 'MACD', description: '平滑异同移动平均线', category: 'momentum', params: [12, 26, 9] },
  { label: 'RSI', value: 'RSI', description: '相对强弱指标', category: 'momentum', params: [14] },
  { label: 'KDJ', value: 'KDJ', description: '随机指标', category: 'momentum', params: [9, 3, 3] },
  { label: 'CCI', value: 'CCI', description: '顺势指标', category: 'momentum', params: [14] }
]

// 波动率指标
const volatilityIndicators: IndicatorMeta[] = [
  { label: 'BOLL', value: 'BOLL', description: '布林带', category: 'volatility', params: [20, 2] },
  { label: 'ATR', value: 'ATR', description: '真实波幅', category: 'volatility', params: [14] }
]

// 成交量指标
const volumeIndicators: IndicatorMeta[] = [
  { label: 'VOL', value: 'VOL', description: '成交量', category: 'volume' },
  { label: 'VOL-MA5', value: 'VOL-MA5', description: '5日成交量均线', category: 'volume', params: [5] },
  { label: 'OBV', value: 'OBV', description: '能量潮', category: 'volume' }
]

// 所有指标元数据映射
const indicatorMetaMap = new Map<string, IndicatorMeta>()
const allIndicators = [
  ...trendIndicators,
  ...momentumIndicators,
  ...volatilityIndicators,
  ...volumeIndicators
]

allIndicators.forEach(indicator => {
  indicatorMetaMap.set(indicator.value, indicator)
})

// Computed
const selectedCount = computed(() => selectedIndicators.value.length)

/**
 * 检查指标是否已选中
 */
const isIndicatorSelected = (indicator: string): CheckboxValueType => {
  return selectedIndicators.value.includes(indicator) as CheckboxValueType
}

/**
 * 获取指标标签
 */
const getIndicatorLabel = (indicator: string): string => {
  const meta = indicatorMetaMap.get(indicator)
  return meta?.label || indicator
}

/**
 * 切换指标选中状态
 */
const handleToggleIndicator = (indicator: string, checked: boolean): void => {
  if (checked) {
    if (!selectedIndicators.value.includes(indicator)) {
      selectedIndicators.value.push(indicator)
    }
  } else {
    const index = selectedIndicators.value.indexOf(indicator)
    if (index > -1) {
      selectedIndicators.value.splice(index, 1)
    }
  }
}

/**
 * 包装器函数，处理Element Plus checkbox的类型问题
 */
const onCheckboxChange = (indicator: string, value: CheckboxValueType): void => {
  handleToggleIndicator(indicator, Boolean(value))
}

/**
 * 移除指标
 */
const handleRemoveIndicator = (indicator: string): void => {
  const index = selectedIndicators.value.indexOf(indicator)
  if (index > -1) {
    selectedIndicators.value.splice(index, 1)
    emitChange()
  }
}

/**
 * 清空所有指标
 */
const handleClearAll = (): void => {
  selectedIndicators.value = []
}

/**
 * 应用指标选择
 */
const handleApply = (): void => {
  emitChange()
  // 关闭 popover (通过点击外部或按ESC)
}

/**
 * 发送变更事件
 */
const emitChange = (): void => {
  emit('update:modelValue', [...selectedIndicators.value])
  emit('change', [...selectedIndicators.value])
}

/**
 * Watch props.modelValue changes
 */
watch(() => props.modelValue, (newValue) => {
  selectedIndicators.value = [...newValue]
})
</script>

<style scoped lang="scss">
.indicator-selector {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  .indicator-badge {
    margin-left: 4px;
  }

  .indicator-panel {
    .indicator-tabs {
      :deep(.el-tabs__content) {
        max-height: 300px;
        overflow-y: auto;
      }

      .indicator-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 8px 0;

        .indicator-item {
          display: flex;
          flex-direction: column;
          gap: 2px;

          .indicator-name {
            font-weight: 500;
            color: var(--el-text-color-primary);
          }

          .indicator-desc {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }

        :deep(.el-checkbox) {
          margin-right: 0;
          width: 100%;

          .el-checkbox__label {
            width: 100%;
            padding-left: 8px;
          }
        }
      }
    }

    .indicator-actions {
      display: flex;
      justify-content: space-between;
      padding-top: 16px;
      border-top: 1px solid var(--el-border-color);
    }
  }

  .selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;

    .el-tag {
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}
</style>
