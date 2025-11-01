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
              type="success"
              effect="dark"
              class="selected-indicator-tag"
              @close="handleRemove(index)"
            >
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
                <p class="indicator-full-name">{{ indicator.full_name }}</p>
                <p class="indicator-chinese-name">{{ indicator.chinese_name }}</p>
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

    <!-- 参数配置对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      title="配置指标参数"
      width="400px"
      append-to-body
    >
      <el-form v-if="currentIndicatorConfig" label-width="120px">
        <el-form-item
          v-for="param in currentIndicatorConfig.parameters"
          :key="param.name"
          :label="param.display_name"
        >
          <el-input-number
            v-model="parameterValues[param.name]"
            :min="param.min"
            :max="param.max"
            :step="param.step || 1"
          />
          <el-text size="small" type="info" style="display: block; margin-top: 4px;">
            {{ param.description }} (默认: {{ param.default }})
          </el-text>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAddIndicator">确认添加</el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
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

const emit = defineEmits(['update:modelValue', 'add-indicator', 'remove-indicator'])

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
        ind.full_name.toLowerCase().includes(query) ||
        ind.chinese_name.includes(query)
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
  ElMessage.success(`已添加指标: ${indicator.chinese_name}`)
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
  ElMessage.success(`已添加指标: ${currentIndicatorConfig.value.chinese_name}`)

  showConfigDialog.value = false
  currentIndicatorConfig.value = null
}

// 移除指标
const handleRemove = (index) => {
  emit('remove-indicator', index)
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
    .map(param => `${param.display_name}(${param.default})`)
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
</style>
