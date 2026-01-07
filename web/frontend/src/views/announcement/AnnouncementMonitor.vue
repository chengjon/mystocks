<template>
  <div class="announcement-monitor">
    <div class="page-header">
      <h1 class="page-title">ANNOUNCEMENT MONITOR</h1>
      <p class="page-subtitle">REAL-TIME ANNOUNCEMENTS | INTELLIGENT ANALYSIS | CUSTOM RULES</p>
    </div>

    <!-- 功能说明 -->
    <el-alert
      title="公告监控功能说明"
      type="info"
      :closable="false"
      show-icon
      class="info-banner"
    >
      <template #default>
        <p>
          本系统提供实时公告监控功能，支持设置自定义规则监控重要公告。
          系统会自动获取巨潮资讯等官方公告信息，对重要事件进行标记和提醒。
        </p>
        <el-space wrap>
          <el-tag>实时获取</el-tag>
          <el-tag>智能分析</el-tag>
          <el-tag>自定义规则</el-tag>
          <el-tag>重要提醒</el-tag>
        </el-space>
      </template>
    </el-alert>

    <div class="stats-grid">
      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.total_count || 0 }}</div>
              <div class="stat-label">公告总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">TODAY</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">IMPORTANT</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card :hoverable="true" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">TRIGGERED</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </div>

    <el-card :hoverable="true" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="股票代码">
          <el-input
            v-model="searchForm.stock_code"
            placeholder="请输入股票代码"
            clearable
            style="width: 120px"
          />
        </el-form-item>

        <el-form-item label="公告类型">
          <el-select
            v-model="searchForm.announcement_type"
            placeholder="请选择公告类型"
            style="width: 150px"
          >
            <el-option value="" label="全部类型" />
            <el-option value="业绩预告" label="业绩预告" />
            <el-option value="分红派息" label="分红派息" />
            <el-option value="重组并购" label="重组并购" />
            <el-option value="风险提示" label="风险提示" />
          </el-select>
        </el-form-item>

        <el-form-item label="重要性">
          <el-select
            v-model="searchForm.min_importance"
            placeholder="重要性级别"
            style="width: 120px"
          >
            <el-option :value="0" label="全部" />
            <el-option :value="1" label="1级" />
            <el-option :value="2" label="2级" />
            <el-option :value="3" label="3级" />
            <el-option :value="4" label="4级" />
            <el-option :value="5" label="5级" />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="fetchAnnouncements" :loading="loading.announcements">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 公告列表 -->
    <el-card class="announcements-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Document /></el-icon>
            公告列表
          </span>
          <div class="card-actions">
            <el-button size="small" @click="fetchTodayAnnouncements">
              <el-icon><Calendar /></el-icon>
              今日公告
            </el-button>
            <el-button size="small" @click="fetchImportantAnnouncements">
              <el-icon><Warning /></el-icon>
              重要公告
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="announcements"
        style="width: 100%"
        v-loading="loading.announcements"
        row-key="id"
      >
        <el-table-column prop="stock_code" label="代码" width="100" fixed="left" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <span :class="getImportanceClass(row.importance_level)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="importance_level" label="重要性" width="100">
          <template #default="{ row }">
            <el-rate
              v-model="row.importance_level"
              :max="5"
              :allow-half="false"
              :show-text="false"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              disabled
              style="line-height: 24px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="sentiment" label="情感倾向" width="100">
          <template #default="{ row }">
            <el-tag :type="getSentimentType(row.sentiment)" size="small">
              {{ formatSentiment(row.sentiment) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布日期" width="120" sortable />
        <el-table-column prop="data_source" label="数据源" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.url"
              size="small"
              type="primary"
              link
              @click="openAnnouncement(row.url)"
            >
              查看原文
            </el-button>
            <el-button
              v-else
              size="small"
              type="info"
              link
              disabled
            >
              无链接
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 监控规则管理 -->
    <el-card class="rules-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Setting /></el-icon>
            监控规则管理
          </span>
          <el-button size="small" type="primary" @click="showRuleDialog = true">
            <el-icon><Plus /></el-icon>
            新增规则
          </el-button>
        </div>
      </template>

      <el-table
        :data="monitorRules"
        style="width: 100%"
        v-loading="loading.rules"
      >
        <el-table-column prop="rule_name" label="规则名称" width="150" />
        <el-table-column prop="stock_codes" label="监控股票" width="150">
          <template #default="{ row }">
            <span v-if="row.stock_codes && row.stock_codes.length > 0">
              {{ row.stock_codes.slice(0, 2).join(', ') }}
              <span v-if="row.stock_codes.length > 2">等{{ row.stock_codes.length }}只</span>
            </span>
            <span v-else>全部股票</span>
          </template>
        </el-table-column>
        <el-table-column prop="keywords" label="关键词" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="keyword in row.keywords.slice(0, 3)"
              :key="keyword"
              size="small"
              style="margin-right: 4px; margin-bottom: 4px;"
            >
              {{ keyword }}
            </el-tag>
            <el-tag v-if="row.keywords.length > 3" size="small" type="info">
              +{{ row.keywords.length - 3 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="min_importance_level" label="最低重要性" width="120">
          <template #default="{ row }">
            <el-rate
              v-model="row.min_importance_level"
              :max="5"
              :allow-half="false"
              :show-text="false"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              disabled
            />
          </template>
        </el-table-column>
        <el-table-column prop="notify_enabled" label="通知" width="80">
          <template #default="{ row }">
            <el-tag :type="row.notify_enabled ? 'success' : 'info'" size="small">
              {{ row.notify_enabled ? '开启' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="editRule(row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="deleteRule(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 规则编辑对话框 -->
      <el-dialog
        v-model="showRuleDialog"
        :title="editingRule.id ? '编辑监控规则' : '新增监控规则'"
        width="600px"
      >
        <el-form :model="editingRule" :rules="ruleFormRules" ref="ruleFormRef" label-width="120px">
          <el-form-item label="规则名称" prop="rule_name">
            <el-input v-model="editingRule.rule_name" placeholder="请输入规则名称" />
          </el-form-item>

          <el-form-item label="监控股票">
            <el-input
              v-model="editingRule.stock_codes_str"
              placeholder="请输入股票代码，逗号分隔（留空表示全部股票）"
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="关键词" prop="keywords_str">
            <el-input
              v-model="editingRule.keywords_str"
              placeholder="请输入关键词，逗号分隔"
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="最低重要性">
            <el-rate
              v-model="editingRule.min_importance_level"
              :max="5"
              :allow-half="false"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
            />
          </el-form-item>

          <el-form-item label="通知设置">
            <el-switch v-model="editingRule.notify_enabled" />
          </el-form-item>

          <el-form-item label="是否启用">
            <el-switch v-model="editingRule.is_active" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showRuleDialog = false">取消</el-button>
            <el-button type="primary" @click="saveRule">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>

    <!-- 已触发监控记录 -->
    <el-card class="records-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Collection /></el-icon>
            触发记录
          </span>
          <el-button size="small" @click="evaluateRules" :loading="loading.evaluation">
            <el-icon><Lightning /></el-icon>
            评估规则
          </el-button>
        </div>
      </template>

      <el-table
        :data="triggeredRecords"
        style="width: 100%"
        v-loading="loading.records"
      >
        <el-table-column prop="rule_name" label="规则名称" width="150" />
        <el-table-column prop="stock_code" label="股票代码" width="100" />
        <el-table-column prop="announcement_title" label="公告标题" min-width="200" />
        <el-table-column prop="matched_keywords" label="匹配关键词" width="150">
          <template #default="{ row }">
            <el-tag
              v-for="keyword in row.matched_keywords"
              :key="keyword"
              size="small"
              style="margin-right: 4px; margin-bottom: 4px;"
            >
              {{ keyword }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggered_at" label="触发时间" width="160" sortable />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Calendar, Warning, Bell, Search, Refresh,
  Setting, Plus, Collection, Lightning
} from '@element-plus/icons-vue'
import axios from 'axios'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 响应式数据
const stats = ref({})
const announcements = ref([])
const monitorRules = ref([])
const triggeredRecords = ref([])

const loading = reactive({
  announcements: false,
  rules: false,
  records: false,
  evaluation: false
})

// 搜索表单
const searchForm = reactive({
  stock_code: '',
  announcement_type: '',
  min_importance: 0,
  dateRange: []
})

// 分页信息
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 规则对话框
const showRuleDialog = ref(false)
const ruleFormRef = ref(null)
const editingRule = ref({
  id: null,
  rule_name: '',
  stock_codes_str: '',
  keywords_str: '',
  min_importance_level: 3,
  notify_enabled: true,
  is_active: true
})

// 规则表单验证
const ruleFormRules = {
  rule_name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  keywords_str: [
    { required: true, message: '请输入关键词', trigger: 'blur' }
  ]
}

// 获取统计信息
const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取统计信息失败')
  }
}

// 获取公告列表
const fetchAnnouncements = async () => {
  loading.announcements = true
  try {
    const params = {
      stock_code: searchForm.stock_code || undefined,
      announcement_type: searchForm.announcement_type || undefined,
      min_importance: searchForm.min_importance > 0 ? searchForm.min_importance : undefined,
      start_date: searchForm.dateRange ? searchForm.dateRange[0] : undefined,
      end_date: searchForm.dateRange ? searchForm.dateRange[1] : undefined,
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const response = await axios.get(`${API_BASE_URL}/api/announcement/list`, { params })

    if (response.data.success) {
      announcements.value = response.data.data
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.data.error || '获取公告列表失败')
    }
  } catch (error) {
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.announcements = false
  }
}

// 获取今日公告
const fetchTodayAnnouncements = async () => {
  loading.announcements = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/today`)

    if (response.data.success) {
      announcements.value = response.data.announcements
      pagination.total = response.data.count
      ElMessage.success(`获取今日公告 ${response.data.count} 条`)
    } else {
      ElMessage.error(response.data.error || '获取今日公告失败')
    }
  } catch (error) {
    console.error('获取今日公告失败:', error)
    ElMessage.error('获取今日公告失败')
  } finally {
    loading.announcements = false
  }
}

// 获取重要公告
const fetchImportantAnnouncements = async () => {
  loading.announcements = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/important`)

    if (response.data.success) {
      announcements.value = response.data.announcements
      pagination.total = response.data.count
      ElMessage.success(`获取重要公告 ${response.data.count} 条`)
    } else {
      ElMessage.error(response.data.error || '获取重要公告失败')
    }
  } catch (error) {
    console.error('获取重要公告失败:', error)
    ElMessage.error('获取重要公告失败')
  } finally {
    loading.announcements = false
  }
}

// 获取监控规则
const fetchMonitorRules = async () => {
  loading.rules = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/monitor-rules`)
    monitorRules.value = response.data
  } catch (error) {
    console.error('获取监控规则失败:', error)
    ElMessage.error('获取监控规则失败')
  } finally {
    loading.rules = false
  }
}

// 获取触发记录
const fetchTriggeredRecords = async () => {
  loading.records = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/announcement/triggered-records`)

    if (response.data.success) {
      triggeredRecords.value = response.data.data
    } else {
      ElMessage.error(response.data.error || '获取触发记录失败')
    }
  } catch (error) {
    console.error('获取触发记录失败:', error)
    ElMessage.error('获取触发记录失败')
  } finally {
    loading.records = false
  }
}

// 评估监控规则
const evaluateRules = async () => {
  loading.evaluation = true
  try {
    const response = await axios.post(`${API_BASE_URL}/api/announcement/monitor/evaluate`)

    if (response.data.success) {
      ElMessage.success(`评估完成，触发 ${response.data.triggered_count} 条规则`)
      fetchTriggeredRecords() // 重新获取触发记录
    } else {
      ElMessage.error(response.data.error || '评估失败')
    }
  } catch (error) {
    console.error('评估监控规则失败:', error)
    ElMessage.error('评估监控规则失败')
  } finally {
    loading.evaluation = false
  }
}

// 编辑规则
const editRule = (rule) => {
  editingRule.value = {
    ...rule,
    stock_codes_str: rule.stock_codes ? rule.stock_codes.join(',') : '',
    keywords_str: rule.keywords ? rule.keywords.join(',') : ''
  }
  showRuleDialog.value = true
}

// 删除规则
const deleteRule = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个监控规则吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await axios.delete(`${API_BASE_URL}/api/announcement/monitor-rules/${id}`)

    if (response.data.success) {
      ElMessage.success('删除成功')
      fetchMonitorRules() // 重新获取规则列表
    } else {
      ElMessage.error(response.data.error || '删除失败')
    }
  } catch (error) {
    console.error('删除规则失败:', error)
    ElMessage.error('删除规则失败')
  }
}

// 保存规则
const saveRule = async () => {
  if (!editingRule.value.rule_name || !editingRule.value.keywords_str) {
    ElMessage.error('请填写必填字段')
    return
  }

  try {
    // 解析股票代码和关键词
    const stockCodes = editingRule.value.stock_codes_str
      ? editingRule.value.stock_codes_str.split(',').map(s => s.trim()).filter(s => s)
      : []
    const keywords = editingRule.value.keywords_str
      .split(',').map(s => s.trim()).filter(s => s)

    const ruleData = {
      rule_name: editingRule.value.rule_name,
      stock_codes: stockCodes,
      keywords: keywords,
      min_importance_level: editingRule.value.min_importance_level,
      notify_enabled: editingRule.value.notify_enabled,
      is_active: editingRule.value.is_active
    }

    let response
    if (editingRule.value.id) {
      // 更新规则
      response = await axios.put(`${API_BASE_URL}/api/announcement/monitor-rules/${editingRule.value.id}`, ruleData)
      ElMessage.success('更新成功')
    } else {
      // 创建规则
      response = await axios.post(`${API_BASE_URL}/api/announcement/monitor-rules`, ruleData)
      ElMessage.success('创建成功')
    }

    // 重新获取规则列表
    fetchMonitorRules()
    showRuleDialog.value = false
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存规则失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 打开公告原文
const openAnnouncement = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

// 获取重要性级别样式类
const getImportanceClass = (level) => {
  if (level >= 4) return 'text-important'
  if (level >= 3) return 'text-medium'
  return 'text-normal'
}

// 获取情感倾向类型
const getSentimentType = (sentiment) => {
  switch (sentiment) {
    case 'positive':
      return 'success'
    case 'negative':
      return 'danger'
    default:
      return 'info'
  }
}

// 格式化情感倾向
const formatSentiment = (sentiment) => {
  const map = {
    'positive': '正面',
    'negative': '负面',
    'neutral': '中性'
  }
  return map[sentiment] || sentiment
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchAnnouncements()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  pagination.page = page
  fetchAnnouncements()
}

// 刷新所有数据
const refreshData = () => {
  fetchStats()
  fetchAnnouncements()
  fetchMonitorRules()
  fetchTriggeredRecords()
}

// 页面加载时获取数据
onMounted(() => {
  refreshData()
})
</script>

<style scoped lang="scss">
.announcement-monitor {
  padding: var(--spacing-6);
  min-height: 100vh;
  background: var(--bg-primary);
  position: relative;
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(
      45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    ),
    repeating-linear-gradient(
      -45deg,
      var(--accent-gold) 0px,
      var(--accent-gold) 1px,
      transparent 1px,
      transparent 10px
    );
}

.page-header {
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;

    .page-title {
      font-family: var(--font-display);
      font-size: var(--font-size-h2);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--tracking-widest);
      color: var(--accent-gold);
      margin: 0 0 var(--spacing-2) 0;
    }

    .page-subtitle {
      font-family: var(--font-body);
      font-size: var(--font-size-small);
      color: var(--fg-muted);
      text-transform: uppercase;
      letter-spacing: var(--tracking-wider);
      margin: 0;
    }
  }

  .info-banner {
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;

    p {
      margin: 0 0 var(--spacing-3) 0;
      line-height: 1.6;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-6);
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;
  }

  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: var(--spacing-4);
      padding: var(--spacing-4);

      .stat-icon {
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(212, 175, 55, 0.1);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: var(--radius-none);

        .el-icon {
          font-size: 28px;
          color: var(--accent-gold);
        }
      }

      .stat-info {
        flex: 1;

        .stat-number {
          font-family: var(--font-mono);
          font-size: var(--font-size-h4);
          font-weight: 700;
          color: var(--fg-primary);
          line-height: 1;

        }

        .stat-label {
          font-family: var(--font-display);
          font-size: var(--font-size-xs);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-wider);
          color: var(--fg-muted);
          margin-top: var(--spacing-2);
        }
      }
    }
  }

  .search-card {
    margin-bottom: var(--spacing-6);
    position: relative;
    z-index: 1;

    .search-form {
      .el-form-item {
        margin-right: 20px;
        margin-bottom: 0;

        &:last-child {
          margin-right: 0;
        }
      }
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .el-icon {
        font-size: 18px;
      }
    }

    .card-actions {
      display: flex;
      gap: 8px;
    }
  }

  .announcements-card,
  .rules-card,
  .records-card {
    margin-bottom: 20px;
  }

  .text-important {
    color: #f56c6c;
    font-weight: bold;
  }

  .text-medium {
    color: #e6a23c;
  }

  .text-normal {
    color: #606266;
  }
</style>
