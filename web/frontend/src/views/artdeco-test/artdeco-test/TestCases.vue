<template>
  <div class="test-cases-container">
    <!-- 测试用例主容器 -->
    <div class="test-cases-header">
      <h2 class="test-cases-title">测试用例</h2>
      <div class="test-cases-actions">
        <button class="btn-primary" @click="refreshTestCases">刷新用例</button>
        <button class="btn-secondary" @click="addTestCase">创建用例</button>
        <button class="btn-secondary" @click="batchExecute">批量执行</button>
        <button class="btn-secondary" @click="exportTestCases">导出用例</button>
      </div>
    </div>

    <!-- 用例筛选面板 -->
    <div class="test-cases-filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <h3>用例筛选</h3>
          <button class="close-btn" @click="toggleFilter">×</button>
        </div>
        <div class="filter-body">
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">用例名称</span>
              <input type="text" v-model="filters.caseName" placeholder="输入用例名称" class="search-input">
            </div>
            <div class="filter-item">
              <span class="filter-label">模块</span>
              <select v-model="filters.module" class="filter-select">
                <option value="all">全部</option>
                <option value="market">市场数据</option>
                <option value="trading">交易</option>
                <option value="risk">风险管理</option>
                <option value="portfolio">投资组合</option>
              </select>
            </div>
          </div>
          <div class="filter-row">
            <div class="filter-item">
              <span class="filter-label">状态</span>
              <select v-model="filters.status" class="filter-select">
                <option value="all">全部</option>
                <option value="pending">待执行</option>
                <option value="running">执行中</option>
                <option value="passed">通过</option>
                <option value="failed">失败</option>
              </select>
            </div>
            <div class="filter-item">
              <span class="filter-label">优先级</span>
              <select v-model="filters.priority" class="filter-select">
                <option value="all">全部</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
          </div>
          <div class="filter-actions">
            <button class="btn-primary" @click="applyFilters">应用筛选</button>
            <button class="btn-secondary" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 用例列表 -->
    <div class="test-cases-list">
      <div class="card test-case-card" v-for="testCase in testCases" :key="testCase.id">
        <div class="card-header" :class="getStatusClass(testCase.status)">
          <span class="case-name">{{ testCase.name }}</span>
          <span class="case-module">{{ testCase.module }}</span>
          <span class="case-priority" :class="getPriorityClass(testCase.priority)">
            {{ getPriorityName(testCase.priority) }}
          </span>
          <span class="case-status" :class="getStatusClass(testCase.status)">
            {{ getStatusName(testCase.status) }}
          </span>
          <div class="case-actions">
            <button class="btn-run" @click="runTestCase(testCase)" :disabled="testCase.status === 'running'">
              {{ testCase.status === 'running' ? '运行中' : '运行' }}
            </button>
            <button class="btn-view" @click="viewTestCase(testCase)">
              查看
            </button>
            <button class="btn-edit" @click="editTestCase(testCase)">
              编辑
            </button>
            <button class="btn-delete" @click="deleteTestCase(testCase)">
              删除
            </button>
          </div>
        </div>
        <div class="card-body">
          <div class="case-details">
            <div class="detail-row">
              <span class="detail-label">描述</span>
              <span class="detail-value">{{ testCase.description }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">执行时间</span>
              <span class="detail-time">{{ testCase.executionTime || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">上次执行</span>
              <span class="detail-time">{{ formatTime(testCase.lastRunTime) }}</span>
            </div>
          </div>
          <div class="case-coverage">
            <div class="coverage-item">
              <span class="coverage-label">覆盖率</span>
              <span class="coverage-value">{{ testCase.coverage }}%</span>
            </div>
            <div class="coverage-item">
              <span class="coverage-label">成功率</span>
              <span class="coverage-value" :class="getSuccessRateClass(testCase.successRate)">
                {{ testCase.successRate }}%
              </span>
            </div>
          </div>
          <div class="case-dependencies">
            <div class="dependencies-list">
              <span class="dependencies-label">依赖用例：</span>
              <div class="dependencies-items">
                <span class="dependency-item" v-for="dep in testCase.dependencies" :key="dep">
                  {{ dep }}
                </span>
                <span class="dependencies-empty" v-if="testCase.dependencies.length === 0">无依赖</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="test-cases-pagination">
      <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
        下一页
      </button>
      <div class="page-size-selector">
        <label class="page-size-label">每页显示:</label>
        <select v-model="pageSize" @change="changePageSize" class="page-size-select">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>
    </div>

    <!-- 创建/编辑用例模态框 -->
    <div class="modal" v-if="showCaseModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑' : '创建' }}测试用例</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">用例名称 *</label>
            <input type="text" v-model="caseForm.name" placeholder="输入用例名称" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">所属模块 *</label>
            <select v-model="caseForm.module" class="form-select">
              <option value="market">市场数据</option>
              <option value="trading">交易</option>
              <option value="risk">风险管理</option>
              <option value="portfolio">投资组合</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">描述 *</label>
            <textarea v-model="caseForm.description" placeholder="输入用例描述" class="form-textarea"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">优先级</label>
            <select v-model="caseForm.priority" class="form-select">
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">超时时间（秒）</label>
            <input type="number" v-model="caseForm.timeout" placeholder="输入超时时间" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">依赖用例</label>
            <textarea v-model="caseForm.dependencies" placeholder="输入依赖用例（每行一个）" class="form-textarea"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="saveTestCase">保存用例</button>
          <button class="btn-secondary" @click="closeModal">取消</button>
        </div>
      </div>
    </div>

    <!-- 批量执行面板 -->
    <div class="batch-execute-panel" v-if="showBatchExecute">
      <div class="card batch-card">
        <div class="card-header">
          <h3>批量执行</h3>
          <button class="close-btn" @click="toggleBatchExecute">×</button>
        </div>
        <div class="card-body">
          <div class="batch-info">
            <div class="info-row">
              <span class="info-label">待执行用例</span>
              <span class="info-value">{{ batchCases.length }}个</span>
            </div>
            <div class="info-row">
              <span class="info-label">预计总时间</span>
              <span class="info-value">{{ estimatedTime }}秒</span>
            </div>
          </div>
          <div class="batch-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: batchProgress + '%' }"></div>
            </div>
            <div class="progress-text">
              {{ batchProgress }}% 完成
            </div>
          </div>
          <div class="batch-results">
            <div class="result-item">
              <span class="result-label">已完成</span>
              <span class="result-value">{{ batchResults.completed }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">通过</span>
              <span class="result-value success">{{ batchResults.passed }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">失败</span>
              <span class="result-value danger">{{ batchResults.failed }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">剩余</span>
              <span class="result-value">{{ batchResults.remaining }}</span>
            </div>
          </div>
          <div class="batch-actions">
            <button class="btn-primary" @click="startBatchExecute" :disabled="isBatchRunning">
              {{ isBatchRunning ? '执行中...' : '开始执行' }}
            </button>
            <button class="btn-secondary" @click="stopBatchExecute" :disabled="!isBatchRunning">
              停止执行
            </button>
            <button class="btn-secondary" @click="viewBatchResults">
              查看结果
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在加载测试用例...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useTestStore } from '@/stores/test'
import { useRouter } from 'vue-router'
import type { TestCase, TestCaseFilters, CaseForm, BatchResults } from '@/types/test'
import { getTestCases, createTestCase, updateTestCase, deleteTestCase, executeTestCase, batchExecuteTestCases, getTestCaseDetail } from '@/api/test'
import { formatTime } from '@/utils/format'

const router = useRouter()
const testStore = useTestStore()

const testCases = ref<TestCase[]>([])
const batchCases = ref<TestCase[]>([])
const batchProgress = ref<number>(0)
const isBatchRunning = ref<boolean>(false)
const estimatedTime = ref<number>(0)

const batchResults = ref<BatchResults>({
  completed: 0,
  passed: 0,
  failed: 0,
  remaining: 0
})

const showCaseModal = ref<boolean>(false)
const showBatchExecute = ref<boolean>(false)
const isEditing = ref<boolean>(false)
const isLoading = ref<boolean>(false)

const filters = reactive<TestCaseFilters>({
  caseName: '',
  module: 'all',
  status: 'all',
  priority: 'all'
})

const caseForm = reactive<CaseForm>({
  id: '',
  name: '',
  module: 'market',
  description: '',
  priority: 'medium',
  timeout: 30,
  dependencies: []
})

const currentPage = ref<number>(1)
const totalPages = ref<number>(10)
const pageSize = ref<number>(20)

const paginatedCases = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return testCases.value.slice(start, end)
})

const refreshTestCases = async () => {
  try {
    isLoading.value = true
    await loadTestCases()
  } catch (error) {
    console.error('Error refreshing test cases:', error)
  } finally {
    isLoading.value = false
  }
}

const loadTestCases = async () => {
  try {
    const response = await getTestCases(filters)
    
    if (response.code === 200 && response.data) {
      testCases.value = response.data.data
      currentPage.value = 1
      totalPages.value = Math.ceil(response.data.data.length / pageSize.value)
    } else {
      console.error('Failed to load test cases:', response.message)
    }
  } catch (error) {
    console.error('Error loading test cases:', error)
    throw error
  }
}

const toggleFilter = () => {
  const filterPanel = document.querySelector('.test-cases-filter-section')
  if (filterPanel) {
    filterPanel.classList.toggle('hidden')
  }
}

const applyFilters = async () => {
  await loadTestCases()
  toggleFilter()
}

const resetFilters = () => {
  filters.caseName = ''
  filters.module = 'all'
  filters.status = 'all'
  filters.priority = 'all'
  applyFilters()
}

const addTestCase = () => {
  isEditing.value = false
  caseForm.id = ''
  caseForm.name = ''
  caseForm.module = 'market'
  caseForm.description = ''
  caseForm.priority = 'medium'
  caseForm.timeout = 30
  caseForm.dependencies = []
  showCaseModal.value = true
}

const editTestCase = (testCase: TestCase) => {
  isEditing.value = true
  caseForm.id = testCase.id
  caseForm.name = testCase.name
  caseForm.module = testCase.module
  caseForm.description = testCase.description
  caseForm.priority = testCase.priority
  caseForm.timeout = testCase.timeout || 30
  caseForm.dependencies = testCase.dependencies || []
  showCaseModal.value = true
}

const closeModal = () => {
  showCaseModal.value = false
  isEditing.value = false
  resetCaseForm()
}

const saveTestCase = async () => {
  try {
    if (isEditing.value) {
      const response = await updateTestCase(caseForm.id, caseForm)
      
      if (response.code === 200) {
        await loadTestCases()
        closeModal()
        console.log('Test case updated successfully')
      } else {
        console.error('Failed to update test case:', response.message)
      }
    } else {
      const response = await createTestCase(caseForm)
      
      if (response.code === 200) {
        await loadTestCases()
        closeModal()
        console.log('Test case created successfully')
      } else {
        console.error('Failed to create test case:', response.message)
      }
    }
  } catch (error) {
    console.error('Error saving test case:', error)
  }
}

const resetCaseForm = () => {
  caseForm.id = ''
  caseForm.name = ''
  caseForm.module = 'market'
  caseForm.description = ''
  caseForm.priority = 'medium'
  caseForm.timeout = 30
  caseForm.dependencies = []
}

const deleteTestCase = async (testCase: TestCase) => {
  try {
    const response = await deleteTestCase(testCase.id)
    
    if (response.code === 200) {
      await loadTestCases()
      console.log('Test case deleted successfully')
    } else {
      console.error('Failed to delete test case:', response.message)
    }
  } catch (error) {
    console.error('Error deleting test case:', error)
  }
}

const runTestCase = async (testCase: TestCase) => {
  try {
    const response = await executeTestCase(testCase.id)
    
    if (response.code === 200) {
      await loadTestCases()
      console.log('Test case executed successfully')
    } else {
      console.error('Failed to execute test case:', response.message)
    }
  } catch (error) {
    console.error('Error executing test case:', error)
  }
}

const viewTestCase = async (testCase: TestCase) => {
  try {
    router.push(`/test/cases/${testCase.id}`)
  } catch (error) {
    console.error('Error navigating to test case:', error)
  }
}

const batchExecute = async () => {
  try {
    const response = await getTestCases({ status: 'pending' })
    
    if (response.code === 200 && response.data) {
      batchCases.value = response.data.data
      estimatedTime.value = response.data.data.reduce((sum, testCase) => sum + (testCase.timeout || 30), 0)
      batchProgress.value = 0
      batchResults.value = {
        completed: 0,
        passed: 0,
        failed: 0,
        remaining: batchCases.value.length
      }
      showBatchExecute.value = true
    }
  } catch (error) {
    console.error('Error preparing batch execute:', error)
  }
}

const toggleBatchExecute = () => {
  showBatchExecute.value = !showBatchExecute.value
}

const startBatchExecute = async () => {
  try {
    isBatchRunning.value = true
    
    const caseIds = batchCases.value.map(c => c.id)
    const response = await batchExecuteTestCases(caseIds)
    
    if (response.code === 200) {
      await loadTestCases()
      isBatchRunning.value = false
      batchProgress.value = 100
      batchResults.value = response.data.data
      console.log('Batch execute completed')
    } else {
      console.error('Failed to batch execute:', response.message)
      isBatchRunning.value = false
    }
  } catch (error) {
    console.error('Error batch executing:', error)
    isBatchRunning.value = false
  }
}

const stopBatchExecute = () => {
  isBatchRunning.value = false
  console.log('Batch execute stopped')
}

const viewBatchResults = () => {
  router.push('/test/batch-results')
}

const exportTestCases = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filters: {
        caseName: filters.caseName,
        module: filters.module,
        status: filters.status,
        priority: filters.priority
      },
      data: testCases.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_cases_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Test cases exported')
  } catch (error) {
    console.error('Error exporting test cases:', error)
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const changePageSize = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  totalPages.value = Math.ceil(testCases.value.length / newSize)
}

const getStatusClass = (status: string) => {
  if (status === 'passed') return 'status-passed'
  if (status === 'failed') return 'status-failed'
  if (status === 'running') return 'status-running'
  if (status === 'pending') return 'status-pending'
  return 'status-unknown'
}

const getStatusName = (status: string) => {
  const names = {
    passed: '通过',
    failed: '失败',
    running: '执行中',
    pending: '待执行',
    unknown: '未知'
  }
  return names[status] || '未知'
}

const getPriorityClass = (priority: string) => {
  if (priority === 'high') return 'priority-high'
  if (priority === 'medium') return 'priority-medium'
  if (priority === 'low') return 'priority-low'
  return 'priority-unknown'
}

const getPriorityName = (priority: string) => {
  const names = {
    high: '高',
    medium: '中',
    low: '低',
    unknown: '未知'
  }
  return names[priority] || '未知'
}

const getSuccessRateClass = (rate: number) => {
  if (rate >= 90) return 'rate-excellent'
  if (rate >= 70) return 'rate-good'
  if (rate >= 50) return 'rate-fair'
  return 'rate-poor'
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '-'
  
  const date = new Date(timestamp)
  return date.toLocaleString()
}

onMounted(async () => {
  await loadTestCases()
  console.log('TestCases component mounted')
})
</script>

<style scoped lang="scss">
.test-cases-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.test-cases-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.test-cases-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.test-cases-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-run,
.btn-view,
.btn-edit,
.btn-delete {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: transparent;
  color: #2196f3;
  border: 1px solid #2196f3;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #2196f3;
}

.btn-run {
  background: #4caf50;
  color: white;
}

.btn-run:hover {
  background: #45a049;
}

.btn-run:disabled {
  background: #e0e0e0;
  color: #ccc;
  cursor: not-allowed;
}

.btn-view {
  background: #2196f3;
  color: white;
}

.btn-view:hover {
  background: #1976d2;
}

.btn-edit {
  background: #ffc107;
  color: white;
}

.btn-edit:hover {
  background: #ffb300;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.btn-delete:hover {
  background: #da190b;
}

.test-cases-filter-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 400px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.filter-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
}

.filter-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.filter-body {
  padding: 20px;
  overflow-y: auto;
}

.filter-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.search-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
  flex-grow: 1;
}

.search-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.filter-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #2196f3;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.test-cases-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.test-case-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.test-case-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header.status-pending {
  background: linear-gradient(135deg, #e0e0e0 0%, #9e9e9e 100%);
}

.card-header.status-running {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
}

.card-header.status-passed {
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
}

.card-header.status-failed {
  background: linear-gradient(135deg, #f44336 0%, #c62828 100%);
}

.case-name {
  font-size: 18px;
  font-weight: bold;
  color: white;
  flex-grow: 1;
}

.case-module {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.case-priority {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 10px;
}

.case-priority.priority-high {
  background: rgba(244, 67, 54, 0.2);
}

.case-priority.priority-medium {
  background: rgba(251, 191, 36, 0.2);
}

.case-priority.priority-low {
  background: rgba(76, 175, 80, 0.2);
}

.case-status {
  font-size: 14px;
  color: white;
  font-weight: 500;
  margin-left: 10px;
}

.case-actions {
  display: flex;
  gap: 5px;
  margin-left: 10px;
}

.btn-run,
.btn-view,
.btn-edit,
.btn-delete {
  padding: 8px 12px;
  font-size: 12px;
}

.card-body {
  padding: 20px;
}

.case-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  flex: 1;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.detail-time {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.case-coverage {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.coverage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.coverage-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.coverage-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.coverage-value.rate-excellent {
  color: #4caf50;
}

.coverage-value.rate-good {
  color: #81c784;
}

.coverage-value.rate-fair {
  color: #ffc107;
}

.coverage-value.rate-poor {
  color: #f44336;
}

.case-dependencies {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.dependencies-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dependencies-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  margin-bottom: 8px;
}

.dependencies-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dependency-item {
  font-size: 14px;
  color: #2196f3;
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
}

.dependencies-empty {
  font-size: 14px;
  color: #999;
  font-style: italic;
}

.test-cases-pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.page-btn {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.page-btn:disabled {
  background: #f0f0f0;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-selector {
  display: flex;
  gap: 10px;
  align-items: center;
}

.page-size-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.page-size-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 500px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
  font-family: 'Courier New', monospace;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 10px;
}

.batch-execute-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 600px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.batch-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.batch-card .card-header {
  background: linear-gradient(135deg, #4caf50 0%, #1b5e20 100%);
  color: white;
  padding: 20px;
}

.batch-card .card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.batch-card .close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 4px;
  padding: 0 10px;
  color: white;
}

.batch-card .card-body {
  padding: 20px;
  overflow-y: auto;
}

.batch-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.batch-progress {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50 0%, #1b5e20 100%);
  transition: width 0.3s;
}

.progress-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-align: center;
  margin-top: 10px;
}

.batch-results {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.result-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.result-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.result-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.result-value.success {
  color: #4caf50;
}

.result-value.danger {
  color: #f44336;
}

.batch-actions {
  display: flex;
  gap: 10px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #2196f3;
  border-top-color: transparent;
  border-right-color: #2196f3;
  border-bottom-color: #2196f3;
  border-left-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .case-coverage {
    grid-template-columns: 1fr;
  }
  
  .batch-results {
    grid-template-columns: 1fr;
  }
}
</style>
