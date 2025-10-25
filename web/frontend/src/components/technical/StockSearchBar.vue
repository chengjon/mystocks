<template>
  <div class="stock-search-bar">
    <el-autocomplete
      v-model="searchInput"
      :fetch-suggestions="queryStockSymbols"
      :placeholder="placeholder"
      :loading="loading"
      :clearable="true"
      value-key="label"
      class="stock-search-input"
      @select="handleSelect"
      @keyup.enter="handleEnter"
    >
      <template #prefix>
        <el-icon class="el-input__icon">
          <Search />
        </el-icon>
      </template>

      <template #default="{ item }">
        <div class="stock-item">
          <span class="stock-symbol">{{ item.symbol }}</span>
          <span class="stock-name">{{ item.name }}</span>
          <el-tag
            v-if="item.exchange"
            :type="item.exchange === 'SH' ? 'primary' : 'success'"
            size="small"
            class="exchange-tag"
          >
            {{ item.exchange }}
          </el-tag>
        </div>
      </template>

      <template #append>
        <el-button
          :icon="Search"
          type="primary"
          :loading="loading"
          @click="handleSearch"
        />
      </template>
    </el-autocomplete>

    <!-- 快速选择 - 常用股票 -->
    <div v-if="showQuickSelect" class="quick-select">
      <el-space wrap>
        <el-tag
          v-for="stock in popularStocks"
          :key="stock.symbol"
          class="quick-select-tag"
          effect="plain"
          @click="selectStock(stock.symbol)"
        >
          {{ stock.symbol }} {{ stock.name }}
        </el-tag>
      </el-space>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入股票代码或名称 (如: 600519 或 茅台)'
  },
  showQuickSelect: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

// 状态
const searchInput = ref(props.modelValue)
const loading = ref(false)

// 常用股票列表
const popularStocks = ref([
  { symbol: '600519.SH', name: '贵州茅台' },
  { symbol: '000001.SZ', name: '平安银行' },
  { symbol: '600036.SH', name: '招商银行' },
  { symbol: '000333.SZ', name: '美的集团' },
  { symbol: '600900.SH', name: '长江电力' }
])

// 模拟股票列表 (实际应该从API获取)
const stockList = ref([
  { symbol: '600519.SH', name: '贵州茅台', exchange: 'SH', label: '600519.SH 贵州茅台' },
  { symbol: '600036.SH', name: '招商银行', exchange: 'SH', label: '600036.SH 招商银行' },
  { symbol: '600900.SH', name: '长江电力', exchange: 'SH', label: '600900.SH 长江电力' },
  { symbol: '601318.SH', name: '中国平安', exchange: 'SH', label: '601318.SH 中国平安' },
  { symbol: '601398.SH', name: '工商银行', exchange: 'SH', label: '601398.SH 工商银行' },
  { symbol: '000001.SZ', name: '平安银行', exchange: 'SZ', label: '000001.SZ 平安银行' },
  { symbol: '000002.SZ', name: '万科A', exchange: 'SZ', label: '000002.SZ 万科A' },
  { symbol: '000333.SZ', name: '美的集团', exchange: 'SZ', label: '000333.SZ 美的集团' },
  { symbol: '000858.SZ', name: '五粮液', exchange: 'SZ', label: '000858.SZ 五粮液' },
  { symbol: '300750.SZ', name: '宁德时代', exchange: 'SZ', label: '300750.SZ 宁德时代' }
])

// 查询股票
const queryStockSymbols = (queryString, callback) => {
  if (!queryString) {
    callback(popularStocks.value.map(stock => ({
      ...stock,
      label: `${stock.symbol} ${stock.name}`
    })))
    return
  }

  // 过滤匹配的股票
  const query = queryString.toLowerCase()
  const results = stockList.value.filter(stock => {
    return (
      stock.symbol.toLowerCase().includes(query) ||
      stock.name.toLowerCase().includes(query) ||
      stock.symbol.replace('.', '').toLowerCase().includes(query)
    )
  })

  callback(results)
}

// 选择股票
const handleSelect = (item) => {
  searchInput.value = item.symbol
  emit('update:modelValue', item.symbol)
  emit('search', item.symbol)
}

// 回车搜索
const handleEnter = () => {
  if (searchInput.value) {
    handleSearch()
  }
}

// 点击搜索按钮
const handleSearch = () => {
  if (!searchInput.value) {
    ElMessage.warning('请输入股票代码')
    return
  }

  // 验证股票代码格式
  if (!validateStockSymbol(searchInput.value)) {
    ElMessage.warning('请输入正确的股票代码格式 (如: 600519.SH 或 000001.SZ)')
    return
  }

  emit('update:modelValue', searchInput.value)
  emit('search', searchInput.value)
}

// 快速选择
const selectStock = (symbol) => {
  searchInput.value = symbol
  emit('update:modelValue', symbol)
  emit('search', symbol)
}

// 验证股票代码格式
const validateStockSymbol = (symbol) => {
  // 允许的格式:
  // 600519.SH, 600519, 000001.SZ, 000001
  const pattern = /^\d{6}(\.(SH|SZ))?$/i

  if (!pattern.test(symbol)) {
    return false
  }

  // 如果没有交易所后缀,尝试自动添加
  if (!symbol.includes('.')) {
    const code = symbol
    if (code.startsWith('6')) {
      searchInput.value = `${code}.SH`
    } else if (code.startsWith('0') || code.startsWith('3')) {
      searchInput.value = `${code}.SZ`
    }
  }

  return true
}

// 监听外部值变化
import { watch } from 'vue'
watch(() => props.modelValue, (newVal) => {
  searchInput.value = newVal
})
</script>

<style scoped lang="scss">
.stock-search-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .stock-search-input {
    width: 400px;

    :deep(.el-input-group__append) {
      padding: 0;

      .el-button {
        margin: 0;
        border-radius: 0 4px 4px 0;
      }
    }
  }

  .stock-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;

    .stock-symbol {
      font-weight: 600;
      color: #303133;
      min-width: 100px;
    }

    .stock-name {
      flex: 1;
      color: #606266;
      font-size: 14px;
    }

    .exchange-tag {
      margin-left: auto;
    }
  }

  .quick-select {
    padding: 8px 0;

    .quick-select-tag {
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .stock-search-bar {
    .stock-search-input {
      width: 100%;
    }
  }
}
</style>
