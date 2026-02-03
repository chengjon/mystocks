<template>
  <el-drawer
    v-model="visible"
    title="技术指标选择"
    direction="rtl"
    size="600px"
    :before-close="handleClose"
  >
    <!-- 抽屉内容 -->
    <div class="indicator-panel">
      <!-- 搜索栏 -->
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索指标名称或缩写..."
          :prefix-icon="Search"
          clearable
        />
      </div>

      <!-- 分类标签 -->
      <div class="category-tabs">
        <el-radio-group v-model="currentCategory" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="trend">趋势</el-radio-button>
          <el-radio-button label="momentum">动量</el-radio-button>
          <el-radio-button label="volatility">波动率</el-radio-button>
          <el-radio-button label="volume">成交量</el-radio-button>
          <el-radio-button label="candlestick">K线形态</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 已选指标 -->
      <div v-if="selectedIndicators.length > 0" class="selected-section">
        <div class="section-header">
          <h4>已选指标 ({{ selectedIndicators.length }})</h4>
          <el-button
            size="small"
            text
            type="danger"
            @click="clearAllIndicators"
          >
            清空全部
          </el-button>
        </div>

        <el-scrollbar max-height="200px">
          <div class="selected-list">
            <el-tag
              v-for="(indicator, index) in selectedIndicators"
              :key="`selected-${index}`"
              closable
              size="large"
              :type="indicator.enabled !== false ? 'success' : 'info'"
              effect="dark"
              class="selected-indicator-tag"
              :style="{ opacity: indicator.enabled !== false ? 1 : 0.6 }"
              @close="handleRemove(index)"
            >
              <el-icon
                :size="14"
                style="margin-right: 6px; cursor: pointer;"
                @click.stop="handleToggleIndicator(index)"
              >
                <component :is="indicator.enabled !== false ? View : Hide" />
              </el-icon>
              <span class="indicator-name">
                {{ indicator.abbreviation }}
                <template v-if="indicator.parameters && indicator.parameters.timeperiod">
                  ({{ indicator.parameters.timeperiod }})
                </template>
              </span>
            </el-tag>
          </div>
        </el-scrollbar>
      </div>

      <!-- 指标列表 -->
      <div class="indicators-section">
        <div class="section-header">
          <h4>可用指标 ({{ filteredIndicators.length }})</h4>
        </div>

        <el-scrollbar height="400px">
          <div class="indicators-grid">
            <el-card
              v-for="indicator in filteredIndicators"
              :key="indicator.abbreviation"
              class="indicator-card"
              shadow="hover"
              @click="selectIndicator(indicator)"
            >
              <template #header>
                <div class="indicator-card-header">
                  <span class="indicator-abbr">{{ indicator.abbreviation }}</span>
                  <el-tag
                    :type="getCategoryTagType(indicator.category)"
                    size="small"
                  >
                    {{ getCategoryLabel(indicator.category) }}
                  </el-tag>
                </div>
              </template>

              <div class="indicator-info">
                <p class="indicator-full-name">{{ indicator.full_name ?? indicator.fullName }}</p>
                <p class="indicator-chinese-name">{{ indicator.chinese_name ?? indicator.chineseName }}</p>
                <p class="indicator-description">{{ indicator.description }}</p>

                <!-- 参数配置 -->
                <div v-if="indicator.parameters && indicator.parameters.length > 0" class="indicator-params">
                  <el-text size="small" type="info">
                    参数: {{ formatParameters(indicator.parameters) }}
                  </el-text>
                </div>
              </div>

              <template #footer>
                <el-button
                  type="primary"
                  size="small"
                  :icon="Plus"
                  @click.stop="addIndicatorWithConfig(indicator)"
                >
                  添加到图表
                </el-button>
              </template>
            </el-card>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <!-- 参数配置对话框 (增强版) -->
    <el-dialog
      v-model="showConfigDialog"
      title="配置指标参数"
      width="500px"
      append-to-body
    >
      <div v-if="currentIndicatorConfig" class="config-dialog-content">
        <!-- 指标信息 -->
        <el-alert
          :title="`${currentIndicatorConfig.chinese_name ?? currentIndicatorConfig.chineseName} (${currentIndicatorConfig.abbreviation})`"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <p class="indicator-desc">{{ currentIndicatorConfig.description }}</p>
        </el-alert>

        <!-- 参数列表 -->
        <el-form label-width="140px" label-position="left">
          <el-form-item
            v-for="param in currentIndicatorConfig.parameters"
            :key="param.name"
            :label="param.displayName"
          >
            <el-space direction="vertical" :size="8" style="width: 100%;">
              <el-space>
                <el-input-number
                  v-model="parameterValues[param.name]"
                  :min="param.min"
                  :max="param.max"
                  :step="param.step || 1"
                  :precision="param.step && param.step < 1 ? 2 : 0"
                  controls-position="right"
                  style="width: 200px;"
                />

                <!-- 快速预设按钮 -->
                <el-button
                  size="small"
                  text
                  @click="resetParameter(param.name, param.default)"
                >
                  重置
                </el-button>
              </el-space>

              <!-- 参数说明 -->
              <div class="param-description">
                <el-text size="small" type="info">
                  <el-icon><InfoFilled /></el-icon>
                  {{ param.description }}
                </el-text>
                <el-text size="small" type="warning" style="display: block; margin-top: 4px;">
                  范围: {{ param.min }} - {{ param.max }} (默认: {{ param.default }})
                </el-text>
              </div>
            </el-space>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-space>
          <el-button @click="showConfigDialog = false">取消</el-button>
          <el-button type="warning" @click="resetAllParameters">重置全部</el-button>
          <el-button type="primary" @click="confirmAddIndicator">确认添加</el-button>
        </el-space>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Search, Plus, View, Hide, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { indicatorService } from '@/services/indicatorService'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  selectedIndicators: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'add-indicator', 'remove-indicator', 'toggle-indicator'])

// 状态
const visible = ref(props.modelValue)
const searchQuery = ref('')
const currentCategory = ref('all')
const availableIndicators = ref([])
const loading = ref(false)

// 参数配置对话框
const showConfigDialog = ref(false)
const currentIndicatorConfig = ref(null)
const parameterValues = ref({})

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

// 监听内部值变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 组件挂载时获取指标列表
onMounted(async () => {
  await fetchIndicatorRegistry()
})

// 获取指标注册表
const fetchIndicatorRegistry = async () => {
  loading.value = true
  try {
    const response = await indicatorService.getRegistry()
    availableIndicators.value = response.indicators || []
  } catch (error) {
    console.error('Failed to fetch indicator registry:', error)
    ElMessage.error('加载指标列表失败')
  } finally {
    loading.value = false
  }
}

// 过滤指标
const filteredIndicators = computed(() => {
  let indicators = availableIndicators.value

  // 分类过滤
  if (currentCategory.value !== 'all') {
    indicators = indicators.filter(ind => ind.category === currentCategory.value)
  }

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    indicators = indicators.filter(ind => {
      return (
        ind.abbreviation.toLowerCase().includes(query) ||
        ind.full_name ?? ind.fullName.toLowerCase().includes(query) ||
        ind.chinese_name ?? ind.chineseName.includes(query)
      )
    })
  }

  return indicators
})

// 选择指标 (快速添加默认参数)
const selectIndicator = (indicator) => {
  // 使用默认参数
  const parameters = {}
  if (indicator.parameters && indicator.parameters.length > 0) {
    indicator.parameters.forEach(param => {
      parameters[param.name] = param.default
    })
  }

  const indicatorSpec = {
    abbreviation: indicator.abbreviation,
    parameters: parameters
  }

  emit('add-indicator', indicatorSpec)
  ElMessage.success(`已添加指标: ${indicator.chinese_name ?? indicator.chineseName}`)
}

// 添加指标并配置参数
const addIndicatorWithConfig = (indicator) => {
  if (indicator.parameters && indicator.parameters.length > 0) {
    // 显示参数配置对话框
    currentIndicatorConfig.value = indicator
    parameterValues.value = {}

    indicator.parameters.forEach(param => {
      parameterValues.value[param.name] = param.default
    })

    showConfigDialog.value = true
  } else {
    // 没有参数,直接添加
    selectIndicator(indicator)
  }
}

// 确认添加指标
const confirmAddIndicator = () => {
  const indicatorSpec = {
    abbreviation: currentIndicatorConfig.value.abbreviation,
    parameters: { ...parameterValues.value }
  }

  emit('add-indicator', indicatorSpec)
  ElMessage.success(`已添加指标: ${currentIndicatorConfig.value.chinese_name ?? currentIndicatorConfig.value.chineseName}`)

  showConfigDialog.value = false
  currentIndicatorConfig.value = null
}

// 移除指标
const handleRemove = (index) => {
  emit('remove-indicator', index)
}

// 增强: 切换指标启用/禁用状态
const handleToggleIndicator = (index) => {
  const indicator = props.selectedIndicators[index]
  const newState = indicator.enabled !== false ? false : true

  emit('toggle-indicator', {
    index: index,
    abbreviation: indicator.abbreviation,
    enabled: newState
  })

  ElMessage.success(`${indicator.abbreviation} ${newState ? '已启用' : '已禁用'}`)
}

// 增强: 重置单个参数到默认值
const resetParameter = (paramName, defaultValue) => {
  parameterValues.value[paramName] = defaultValue
  ElMessage.info(`参数 ${paramName} 已重置为 ${defaultValue}`)
}

// 增强: 重置所有参数到默认值
const resetAllParameters = () => {
  if (!currentIndicatorConfig.value) return

  currentIndicatorConfig.value.parameters.forEach(param => {
    parameterValues.value[param.name] = param.default
  })

  ElMessage.success('所有参数已重置为默认值')
}

// 清空所有指标
const clearAllIndicators = () => {
  for (let i = props.selectedIndicators.length - 1; i >= 0; i--) {
    emit('remove-indicator', i)
  }
  ElMessage.success('已清空所有指标')
}

// 关闭抽屉
const handleClose = (done) => {
  done()
}

// 获取分类标签类型
const getCategoryTagType = (category) => {
  const typeMap = {
    trend: 'primary',
    momentum: 'success',
    volatility: 'warning',
    volume: 'info',
    candlestick: 'danger'
  }
  return typeMap[category] || 'info'
}

// 获取分类标签文本
const getCategoryLabel = (category) => {
  const labelMap = {
    trend: '趋势',
    momentum: '动量',
    volatility: '波动率',
    volume: '成交量',
    candlestick: 'K线形态'
  }
  return labelMap[category] || category
}

// 格式化参数
const formatParameters = (parameters) => {
  if (!parameters || parameters.length === 0) return '无'

  return parameters
    .map(param => `${param.displayName}(${param.default})`)
    .join(', ')
}
</script>

<style scoped lang="scss">
.indicator-panel {
  padding: 0 4px;
  display: flex;
  flex-direction: column;
  gap: 20px;

  .search-section {
    padding: 0;
  }

  .category-tabs {
    :deep(.el-radio-group) {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
  }

  .selected-section {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 8px;

    .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;

      h4 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }
    }

    .selected-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .selected-indicator-tag {
        cursor: pointer;

        .indicator-name {
          font-weight: 600;
        }
      }
    }
  }

  .indicators-section {
    .section-header {
      margin-bottom: 12px;

      h4 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }
    }

    .indicators-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;

      .indicator-card {
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .indicator-card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;

          .indicator-abbr {
            font-size: 16px;
            font-weight: 700;
            color: #409eff;
          }
        }

        .indicator-info {
          padding: 8px 0;

          .indicator-full-name {
            font-size: 14px;
            font-weight: 600;
            color: #303133;
            margin: 0 0 4px 0;
          }

          .indicator-chinese-name {
            font-size: 13px;
            color: #606266;
            margin: 0 0 8px 0;
          }

          .indicator-description {
            font-size: 12px;
            color: #909399;
            line-height: 1.6;
            margin: 0 0 8px 0;
          }

          .indicator-params {
            padding-top: 8px;
            border-top: 1px solid #ebeef5;
          }
        }
      }
    }
  }
}

// 增强: 参数配置对话框样式
.config-dialog-content {
  .indicator-desc {
    margin: 8px 0 0 0;
    font-size: 14px;
    line-height: 1.6;
    color: #606266;
  }

  .param-description {
    .el-text {
      display: flex;
      align-items: center;
      gap: 4px;

      .el-icon {
        flex-shrink: 0;
      }
    }
  }
}
</style>
