<template>
  <div class="stocks">
    <el-card>
      <template #header>
        <div class="header-section">
          <h2>股票列表</h2>
          
          <!-- 筛选条件区域 -->
          <div class="filter-section">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input
                  v-model="filters.search"
                  placeholder="搜索股票代码或名称"
                  clearable
                  @keyup.enter="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-col>
              
              <el-col :span="4">
                <el-select 
                  v-model="filters.industry" 
                  placeholder="选择行业" 
                  clearable
                  @change="handleFilterChange"
                >
                  <el-option
                    v-for="industry in industries"
                    :key="industry.industry_code"
                    :label="industry.industry_name"
                    :value="industry.industry_name"
                  />
                </el-select>
              </el-col>
              
              <el-col :span="4">
                <el-select 
                  v-model="filters.concept" 
                  placeholder="选择概念" 
                  clearable
                  @change="handleFilterChange"
                >
                  <el-option
                    v-for="concept in concepts"
                    :key="concept.concept_code"
                    :label="concept.concept_name"
                    :value="concept.concept_name"
                  />
                </el-select>
              </el-col>
              
              <el-col :span="4">
                <el-select 
                  v-model="filters.market" 
                  placeholder="选择市场" 
                  clearable
                  @change="handleFilterChange"
                >
                  <el-option label="上海" value="SH" />
                  <el-option label="深圳" value="SZ" />
                </el-select>
              </el-col>
              
              <el-col :span="6">
                <div class="filter-actions">
                  <el-button type="primary" @click="handleSearch">搜索</el-button>
                  <el-button @click="handleReset">重置</el-button>
                  <el-button type="success" @click="handleRefresh" :loading="loading">刷新</el-button>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </template>

      <!-- 排序和显示选项 -->
      <div class="table-options">
        <div class="left-options">
          <el-select 
            v-model="sortConfig.field" 
            placeholder="排序字段" 
            style="width: 120px; margin-right: 10px"
            @change="handleSortChange"
          >
            <el-option label="股票代码" value="symbol" />
            <el-option label="股票名称" value="name" />
            <el-option label="行业" value="industry" />
            <el-option label="价格" value="price" />
            <el-option label="涨跌幅" value="change_pct" />
            <el-option label="换手率" value="turnover" />
            <el-option label="成交量" value="volume" />
          </el-select>
          
          <el-select 
            v-model="sortConfig.order" 
            placeholder="排序方式" 
            style="width: 100px"
            @change="handleSortChange"
          >
            <el-option label="升序" value="asc" />
            <el-option label="降序" value="desc" />
          </el-select>
        </div>
        
        <div class="right-options">
          <span class="total-info">共找到 {{ total }} 只股票</span>
        </div>
      </div>

      <!-- 股票列表表格 -->
      <el-table 
        :data="stocks" 
        stripe 
        v-loading="loading" 
        @row-click="handleRowClick"
        highlight-current-row
        class="stocks-table"
      >
        <el-table-column prop="symbol" label="股票代码" width="120" />
        <el-table-column prop="name" label="股票名称" width="150" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="market" label="市场" width="80">
          <template #default="{ row }">
            <el-tag :type="row.market === 'SH' ? 'primary' : 'success'" size="small">
              {{ row.market }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100" sortable="custom">
          <template #default="{ row }">
            <span class="price">{{ row.price || '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change" label="涨跌额" width="100" sortable="custom">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change)">
              {{ row.change ? (row.change > 0 ? '+' : '') + row.change : '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="change_pct" label="涨跌幅(%)" width="120" sortable="custom">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_pct)">
              {{ row.change_pct ? (row.change_pct > 0 ? '+' : '') + row.change_pct + '%' : '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="120" sortable="custom">
          <template #default="{ row }">
            <span>{{ row.volume ? formatVolume(row.volume) : '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="turnover" label="换手率(%)" width="120" sortable="custom">
          <template #default="{ row }">
            <span>{{ row.turnover ? row.turnover + '%' : '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click.stop="handleView(row)">查看</el-button>
            <el-button type="info" size="small" @click.stop="handleAnalyze(row)">分析</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { dataApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

// 筛选条件
const filters = reactive({
  search: '',
  industry: '',
  concept: '',
  market: ''
})

// 行业和概念列表
const industries = ref([])
const concepts = ref([])

// 排序配置
const sortConfig = reactive({
  field: '',
  order: 'desc'
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

// 股票数据
const stocks = ref([])
const total = ref(0)

// 加载筛选选项数据
const loadFilterOptions = async () => {
  try {
    const [industriesRes, conceptsRes] = await Promise.all([
      dataApi.getStocksIndustries(),
      dataApi.getStocksConcepts()
    ])
    
    if (industriesRes.success) {
      industries.value = industriesRes.data
    }
    
    if (conceptsRes.success) {
      concepts.value = conceptsRes.data
    }
  } catch (error) {
    console.error('加载筛选选项失败:', error)
    ElMessage.error('加载筛选选项失败')
  }
}

// 加载股票数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      limit: pagination.pageSize,
      offset: (pagination.currentPage - 1) * pagination.pageSize
    }
    
    // 添加筛选参数
    if (filters.search) {
      params.search = filters.search
    }
    if (filters.industry) {
      params.industry = filters.industry
    }
    if (filters.concept) {
      params.concept = filters.concept
    }
    if (filters.market) {
      params.market = filters.market
    }
    
    // 添加排序参数
    if (sortConfig.field && sortConfig.order) {
      params.sort_field = sortConfig.field
      params.sort_order = sortConfig.order
    }
    
    const response = await dataApi.getStocksBasic(params)
    if (response.success && response.data) {
      stocks.value = response.data
      total.value = response.total || response.data.length
    } else {
      throw new Error(response.msg || 'API返回数据格式错误')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    // 提供更友好的错误信息
    if (error.response) {
      ElMessage.error(`加载数据失败: ${error.response.data?.msg || error.response.data?.detail || '服务器错误'}`)
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查服务是否正常运行')
    } else {
      ElMessage.error(`加载数据失败: ${error.message}`)
    }
  } finally {
    loading.value = false
  }
}

// 事件处理函数
const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  // 重置所有筛选条件
  filters.search = ''
  filters.industry = ''
  filters.concept = ''
  filters.market = ''
  sortConfig.field = ''
  sortConfig.order = 'desc'
  pagination.currentPage = 1
  loadData()
}

const handleFilterChange = () => {
  pagination.currentPage = 1
  loadData()
}

const handleRefresh = () => {
  loadData()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  loadData()
}

const handleSortChange = () => {
  pagination.currentPage = 1
  loadData()
}

const handleView = (row) => {
  router.push({ name: 'stock-detail', params: { symbol: row.symbol }, query: { name: row.name } })
}

const handleAnalyze = (row) => {
  ElMessage.info(`分析股票: ${row.name} (${row.symbol})`)
}

// 行点击事件
const handleRowClick = (row) => {
  handleView(row)
}

// 工具函数
const getChangeClass = (value) => {
  if (value === null || value === undefined || value === '--') return ''
  return value > 0 ? 'text-red' : value < 0 ? 'text-green' : ''
}

const formatVolume = (volume) => {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(1) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(1) + '万'
  }
  return volume.toString()
}

// 初始化
onMounted(async () => {
  await loadFilterOptions()
  await loadData()
})
</script>

<style scoped lang="scss">
.stocks {
  .header-section {
    h2 {
      margin: 0 0 20px;
      color: #303133;
      font-size: 20px;
      font-weight: 600;
    }
  }

  .filter-section {
    margin-bottom: 20px;
    padding: 16px;
    background-color: #f5f7fa;
    border-radius: 6px;
    
    .filter-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .table-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding: 0 4px;
    
    .left-options {
      display: flex;
      align-items: center;
    }
    
    .right-options {
      .total-info {
        color: #606266;
        font-size: 14px;
      }
    }
  }

  .stocks-table {
    .text-red {
      color: #f56c6c;
      font-weight: 500;
    }
    
    .text-green {
      color: #67c23a;
      font-weight: 500;
    }
    
    .price {
      font-weight: 600;
      color: #303133;
    }
  }

  // Element Plus 组件样式覆盖
  :deep(.el-table) {
    .el-table__row {
      cursor: pointer;
      
      &:hover {
        background-color: #f5f7fa;
      }
    }
    
    .el-table__header {
      th {
        background-color: #fafafa;
        font-weight: 600;
      }
    }
  }
}
</style>
