<template>
  <div class="technical-analysis">
    <!-- 头部工具栏 -->
    <div class="toolbar">
      <StockSearchBar
        v-model="selectedSymbol"
        @search="handleStockSearch"
      />

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :shortcuts="dateRangeShortcuts"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        class="date-picker"
        @change="handleDateRangeChange"
      />

      <!-- 周期切换 -->
      <el-radio-group v-model="selectedPeriod" size="default" @change="fetchKlineData" class="period-selector">
        <el-radio-button label="day">日线</el-radio-button>
        <el-radio-button label="week">周线</el-radio-button>
        <el-radio-button label="month">月线</el-radio-button>
      </el-radio-group>

      <el-button
        type="primary"
        :icon="Refresh"
        :loading="loading"
        @click="refreshData"
      >
        刷新数据
      </el-button>

      <el-button
        type="warning"
        :icon="Refresh"
        :loading="loading"
        @click="handleRetry"
      >
        重试
      </el-button>

      <el-button
        :icon="Setting"
        @click="showIndicatorPanel = true"
      >
        指标设置
      </el-button>

      <el-dropdown @command="handleConfigCommand">
        <el-button :icon="FolderOpened">
          配置管理 <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="save">
              <el-icon><DocumentAdd /></el-icon>
              保存当前配置
            </el-dropdown-item>
            <el-dropdown-item command="load">
              <el-icon><FolderOpened /></el-icon>
              加载已保存配置
            </el-dropdown-item>
            <el-dropdown-item command="manage" divided>
              <el-icon><Files /></el-icon>
              管理我的配置
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- K线图表区域 -->
    <div class="chart-container">
      <KLineChart
        v-if="chartData.ohlcv"
        :ohlcv-data="chartData.ohlcv"
        :indicators="chartData.indicators"
        :loading="loading"
        @indicator-remove="handleIndicatorRemove"
      />

      <el-empty
        v-else
        description="请选择股票代码和日期范围开始分析"
        :image-size="200"
      />
    </div>

    <!-- 指标选择面板 -->
    <IndicatorPanel
      v-model="showIndicatorPanel"
      :selected-indicators="selectedIndicators"
      @add-indicator="handleAddIndicator"
      @remove-indicator="handleRemoveIndicator"
    />

    <!-- 数据统计信息 -->
    <div v-if="chartData.ohlcv" class="stats-bar">
      <el-space :size="20">
        <span>
          <el-text tag="b">股票代码:</el-text>
          {{ chartData.symbol }} ({{ chartData.symbolName }})
        </span>
        <span>
          <el-text tag="b">数据点数:</el-text>
          {{ chartData.ohlcv.dates.length }}
        </span>
        <span>
          <el-text tag="b">计算耗时:</el-text>
          {{ chartData.calculationTime }}ms
        </span>
        <span>
          <el-text tag="b">已添加指标:</el-text>
          {{ selectedIndicators.length }}
        </span>
      </el-space>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { Refresh, Setting, FolderOpened, DocumentAdd, Files, ArrowDown } from '@element-plus/icons-vue'
import StockSearchBar from '@/components/technical/StockSearchBar.vue'
import KLineChart from '@/components/technical/KLineChart.vue'
import IndicatorPanel from '@/components/technical/IndicatorPanel.vue'
import { indicatorService, handleIndicatorError } from '@/services/indicatorService.ts'
import { dataApi } from '@/api/index.js'
import { calculateTechnicalIndicators } from '@/utils/technicalIndicators.js'

// 状态管理
const loading = ref(false)
const selectedSymbol = ref('')
const dateRange = ref([])
const showIndicatorPanel = ref(false)
const selectedPeriod = ref('day') // 新增周期选择

// 选中的指标列表
const selectedIndicators = ref([
  // 默认添加MA5和MA10
  { abbreviation: 'SMA', parameters: { timeperiod: 5 } },
  { abbreviation: 'SMA', parameters: { timeperiod: 10 } }
])

// 图表数据
const chartData = reactive({
  symbol: '',
  symbolName: '',
  ohlcv: null,
  indicators: [],
  calculationTime: 0
})

// 添加重试机制
const handleRetry = async () => {
  if (selectedSymbol.value && dateRange.value && dateRange.value.length === 2) {
    await fetchKlineData()
  } else {
    ElMessage.warning('请先选择股票代码和日期范围')
  }
}

// 日期范围快捷选项
const dateRangeShortcuts = [
  {
    text: '最近1个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 1)
      return [start, end]
    }
  },
  {
    text: '最近3个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 3)
      return [start, end]
    }
  },
  {
    text: '最近6个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 6)
      return [start, end]
    }
  },
  {
    text: '最近1年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setFullYear(start.getFullYear() - 1)
      return [start, end]
    }
  }
]

// 处理股票搜索
const handleStockSearch = async (symbol) => {
  selectedSymbol.value = symbol

  // 如果没有选择日期范围，默认最近3个月
  if (!dateRange.value || dateRange.value.length === 0) {
    const end = new Date()
    const start = new Date()
    start.setMonth(start.getMonth() - 3)
    dateRange.value = [
      start.toISOString().split('T')[0],
      end.toISOString().split('T')[0]
    ]
  }

  await fetchKlineData()
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  if (selectedSymbol.value && dateRange.value && dateRange.value.length === 2) {
    fetchKlineData()
  }
}

// 刷新数据
const refreshData = () => {
  if (selectedSymbol.value && dateRange.value && dateRange.value.length === 2) {
    fetchKlineData()
  } else {
    ElMessage.warning('请先选择股票代码和日期范围')
  }
}

// 获取K线数据并计算技术指标
const fetchKlineData = async () => {
  if (!selectedSymbol.value) {
    ElMessage.warning('请输入股票代码')
    return
  }

  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true

  try {
    // 调用K线API (使用market/kline端点)
    const response = await dataApi.getKline({
      symbol: selectedSymbol.value,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      period: selectedPeriod.value,
      adjust: 'qfq' // 使用前复权
    })

    if (response.success && response.data && response.data.length > 0) {
      // 转换数据格式以匹配现有图表组件 (处理market/kline返回的数据格式)
      const dates = response.data.map(item => item.date)
      const opens = response.data.map(item => item.open)
      const highs = response.data.map(item => item.high)
      const lows = response.data.map(item => item.low)
      const closes = response.data.map(item => item.close)
      const volumes = response.data.map(item => item.volume)

      // 更新图表数据
      chartData.symbol = response.stock_code || selectedSymbol.value
      chartData.symbolName = response.stock_name || selectedSymbol.value
      chartData.ohlcv = {
        dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        volume: volumes
      }

      // 计算技术指标
      const startTime = performance.now();
      const calculatedIndicators = calculateTechnicalIndicators(
        chartData.ohlcv,
        selectedIndicators.value
      );
      const endTime = performance.now();

      // 将计算结果转换为图表组件需要的格式
      const indicatorsResult = Object.keys(calculatedIndicators).map(key => {
        const values = calculatedIndicators[key];
        return {
          abbreviation: key,
          parameters: {},
          outputs: [{
            output_name: key,
            values: values,
            display_name: key
          }],
          panel_type: key.includes('rsi') || key.includes('macd') ? 'separate' : 'overlay'
        };
      });

      chartData.indicators = indicatorsResult;
      chartData.calculationTime = Math.round(endTime - startTime);

      ElNotification({
        title: '数据加载成功',
        message: `成功加载 ${response.total} 个数据点，计算 ${selectedIndicators.value.length} 个指标`,
        type: 'success',
        duration: 2000
      })
    } else {
      ElMessage.info('未找到该股票的历史数据')
      // 清空图表数据
      chartData.ohlcv = null
    }
  } catch (error) {
    console.error('Failed to fetch kline data:', error)
    const errorMessage = error.response?.data?.msg || error.message || '获取K线数据失败'

    ElNotification({
      title: '数据加载失败',
      message: errorMessage,
      type: 'error',
      duration: 3000
    })

    // 如果是404错误(数据未找到)，提供友好提示
    if (error.response?.status === 404) {
      ElMessage.info('数据库中暂无该股票的历史数据')
    }
  } finally {
    loading.value = false
  }
}

// 添加指标
const handleAddIndicator = (indicator) => {
  selectedIndicators.value.push(indicator)

  // 如果已经有数据，重新加载
  if (chartData.ohlcv) {
    fetchKlineData()
  }
}

// 移除指标
const handleRemoveIndicator = (index) => {
  selectedIndicators.value.splice(index, 1)

  // 如果已经有数据，重新加载
  if (chartData.ohlcv) {
    fetchKlineData()
  }
}

// 从图表移除指标
const handleIndicatorRemove = (indicatorIndex) => {
  handleRemoveIndicator(indicatorIndex)
}

// 组件挂载时初始化
onMounted(() => {
  // 可以从URL参数或localStorage恢复上次的选择
  const cachedSymbol = localStorage.getItem('lastSelectedSymbol')
  const cachedDateRange = localStorage.getItem('lastDateRange')

  if (cachedSymbol) {
    selectedSymbol.value = cachedSymbol
  }

  if (cachedDateRange) {
    try {
      dateRange.value = JSON.parse(cachedDateRange)
    } catch (e) {
      console.error('Failed to parse cached date range:', e)
    }
  }
})

// 保存用户选择到localStorage
const saveToLocalStorage = () => {
  if (selectedSymbol.value) {
    localStorage.setItem('lastSelectedSymbol', selectedSymbol.value)
  }
  if (dateRange.value) {
    localStorage.setItem('lastDateRange', JSON.stringify(dateRange.value))
  }
}

// 监听变化并保存
watch([selectedSymbol, dateRange], saveToLocalStorage)

// 配置管理功能
const handleConfigCommand = async (command) => {
  switch (command) {
    case 'save':
      await handleSaveConfig()
      break
    case 'load':
      await handleLoadConfig()
      break
    case 'manage':
      await handleManageConfigs()
      break
  }
}

// 保存当前配置
const handleSaveConfig = async () => {
  if (selectedIndicators.value.length === 0) {
    ElMessage.warning('当前没有选择任何指标')
    return
  }

  ElMessageBox.prompt('请输入配置名称', '保存指标配置', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '配置名称不能为空'
  }).then(async ({ value }) => {
    try {
      await indicatorService.createConfig({
        name: value,
        indicators: selectedIndicators.value
      })

      ElMessage.success(`配置"${value}"已保存`)
    } catch (error) {
      console.error('Failed to save config:', error)
      const errorMessage = handleIndicatorError(error)
      ElMessage.error(`保存失败: ${errorMessage}`)
    }
  }).catch(() => {
    // 用户取消
  })
}

// 加载已保存配置
const handleLoadConfig = async () => {
  try {
    const response = await indicatorService.listConfigs()

    if (response.total_count === 0) {
      ElMessage.info('暂无已保存的配置')
      return
    }

    // 创建配置选择列表
    const configOptions = response.configs.map(config => ({
      label: `${config.name} (${config.indicators.length}个指标)`,
      value: config.id
    }))

    ElMessageBox({
      title: '加载配置',
      message: '选择要加载的配置',
      showCancelButton: true,
      confirmButtonText: '加载',
      cancelButtonText: '取消',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          const selectedConfigId = instance.inputValue
          if (!selectedConfigId) {
            ElMessage.warning('请选择一个配置')
            return
          }

          indicatorService.getConfig(parseInt(selectedConfigId))
            .then(config => {
              selectedIndicators.value = config.indicators
              ElMessage.success(`已加载配置"${config.name}"`)

              // 如果已有数据，重新加载
              if (chartData.ohlcv) {
                fetchKlineData()
              }

              done()
            })
            .catch(error => {
              console.error('Failed to load config:', error)
              ElMessage.error('加载失败')
            })
        } else {
          done()
        }
      }
    }).catch(() => {
      // 用户取消
    })
  } catch (error) {
    console.error('Failed to list configs:', error)
    ElMessage.error('获取配置列表失败')
  }
}

// 管理配置
const handleManageConfigs = async () => {
  try {
    const response = await indicatorService.listConfigs()

    if (response.total_count === 0) {
      ElMessage.info('暂无已保存的配置')
      return
    }

    // 显示配置列表
    const configListHtml = response.configs.map(config => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #ebeef5;">
        <div>
          <strong>${config.name}</strong>
          <small style="color: #909399; margin-left: 8px;">${config.indicators.length}个指标</small>
        </div>
        <div>
          <button class="el-button el-button--text el-button--small" onclick="deleteConfig(${config.id})">删除</button>
        </div>
      </div>
    `).join('')

    ElMessageBox({
      title: '配置管理',
      message: `<div>${configListHtml}</div>`,
      dangerouslyUseHTMLString: true,
      showCancelButton: true,
      confirmButtonText: '关闭',
      cancelButtonText: '刷新',
      beforeClose: (action, instance, done) => {
        if (action === 'cancel') {
          handleManageConfigs() // 刷新列表
        } else {
          done()
        }
      }
    })
  } catch (error) {
    console.error('Failed to manage configs:', error)
    ElMessage.error('获取配置列表失败')
  }
}

// 删除配置（需要在全局暴露）
window.deleteConfig = async (configId) => {
  try {
    await ElMessageBox.confirm('确认删除该配置吗？', '提示', {
      type: 'warning'
    })

    await indicatorService.deleteConfig(configId)
    ElMessage.success('配置已删除')

    // 重新打开管理面板
    setTimeout(() => handleManageConfigs(), 300)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete config:', error)
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped lang="scss">
.technical-analysis {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: #f5f7fa;

  .toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

    .date-picker {
      width: 320px;
    }

    .period-selector {
      margin-left: 12px;
    }
  }

  .chart-container {
    flex: 1;
    min-height: 500px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    padding: 20px;
    overflow: hidden;
  }

  .stats-bar {
    margin-top: 16px;
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

    .el-text {
      margin-right: 8px;
      color: #606266;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .technical-analysis {
    padding: 10px;

    .toolbar {
      flex-wrap: wrap;
      gap: 8px;

      .date-picker {
        width: 100%;
      }
    }

    .chart-container {
      min-height: 400px;
    }
  }
}
</style>
