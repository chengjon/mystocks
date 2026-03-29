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
          v-for="(stock, _idx) in popularStocks"
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
import { ref, watch } from 'vue'
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

watch(() => props.modelValue, (newVal) => {
  searchInput.value = newVal
})
</script>

<style scoped lang="scss">
@use '../../styles/artdeco-tokens.scss' as *;

.stock-search-bar {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);

  .stock-search-input {
    width: 100%;

    :deep(.el-input__wrapper) {
      background: color-mix(in srgb, var(--artdeco-bg-global) 88%, var(--artdeco-bg-card));
      box-shadow: inset 0 0 0 var(--artdeco-spacing-px) var(--artdeco-border-default);
    }

    :deep(.el-input__inner) {
      color: var(--artdeco-fg-primary);
    }

    :deep(.el-input__inner::placeholder) {
      color: var(--artdeco-fg-muted);
    }

    :deep(.el-input__icon) {
      color: var(--artdeco-gold-primary);
    }

    :deep(.el-input-group__append) {
      padding: 0;
      background: transparent;
      border: none;

      .el-button {
        margin: 0;
        border-radius: 0 var(--artdeco-radius-none) var(--artdeco-radius-none) 0;
        border-color: var(--artdeco-gold-primary);
        background: var(--artdeco-gold-primary);
        color: var(--artdeco-bg-global);
      }

      .el-button:hover {
        border-color: var(--artdeco-gold-light);
        background: var(--artdeco-gold-light);
      }
    }
  }

  .stock-item {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-1) 0;

    .stock-symbol {
      min-width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5));
      color: var(--artdeco-fg-primary);
      font-weight: var(--artdeco-font-semibold);
    }

    .stock-name {
      flex: 1;
      color: var(--artdeco-fg-muted);
      font-size: var(--artdeco-text-sm);
    }

    .exchange-tag {
      margin-left: auto;
    }
  }

  .quick-select {
    padding: var(--artdeco-spacing-2) 0;

    .quick-select-tag {
      cursor: pointer;
      color: var(--artdeco-fg-primary);
      border-color: var(--artdeco-border-default);
      background: color-mix(in srgb, var(--artdeco-gold-primary) 8%, var(--artdeco-bg-card));
      transition:
        transform var(--artdeco-transition-quick) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
        color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-out);

      &:hover {
        transform: translateY(calc(var(--artdeco-spacing-px) * -2));
        box-shadow: var(--artdeco-shadow-md);
        color: var(--artdeco-gold-primary);
        border-color: var(--artdeco-gold-primary);
      }
    }
  }
}
</style>
