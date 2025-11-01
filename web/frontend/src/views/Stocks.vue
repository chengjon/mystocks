<template>
  <div class="stocks">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>股票管理</span>
          <div>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索股票代码或名称"
              style="width: 200px; margin-right: 10px"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="small" @click="handleSearch">搜索</el-button>
            <el-button type="success" size="small" @click="handleRefresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="stocks" stripe v-loading="loading">
        <el-table-column prop="symbol" label="股票代码" width="120" />
        <el-table-column prop="name" label="股票名称" width="150" />
        <el-table-column prop="industry" label="所属行业" />
        <el-table-column prop="area" label="地区" width="100" />
        <el-table-column prop="market" label="市场" width="100" />
        <el-table-column prop="list_date" label="上市日期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button type="info" size="small" @click="handleAnalyze(row)">分析</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
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
import { ref, onMounted } from 'vue'
import { dataApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const searchKeyword = ref('')
const stocks = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadData = async () => {
  loading.value = true
  try {
    const response = await dataApi.getStocksBasic({
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value
    })
    if (response.data) {
      stocks.value = response.data
      total.value = response.total || response.data.length
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleRefresh = () => {
  searchKeyword.value = ''
  currentPage.value = 1
  loadData()
}

const handleSizeChange = () => {
  loadData()
}

const handleCurrentChange = () => {
  loadData()
}

const handleView = (row) => {
  ElMessage.info(`查看股票: ${row.name} (${row.symbol})`)
}

const handleAnalyze = (row) => {
  ElMessage.info(`分析股票: ${row.name} (${row.symbol})`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.stocks {
  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
