<template>
    <PageHeader
      title="告警规则管理"
      subtitle="ALERT RULES MANAGEMENT"
    >
      <template #description>
        设置和管理股票监控告警规则
      </template>
      <template #actions>
        <button class="button button-primary" @click="showCreateDialog = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          新建规则
        </button>
        <button class="button" @click="fetchAlertRules" :class="{ loading: loading }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          刷新
        </button>
      </template>
    </PageHeader>

    <div class="card rules-card">
      <div class="card-body">
        <StockListTable
          :columns="tableColumns"
          :data="paginatedRules"
          :loading="loading"
          :row-clickable="false"
        >
          <template #cell-rule_type="{ row }">
            <el-tag :type="getRuleTypeTag(row.rule_type)">
              {{ formatRuleType(row.rule_type) }}
            </el-tag>
          </template>
          <template #cell-parameters="{ row }">
            <div class="param-display">
              <span v-for="(value, key) in row.parameters" :key="key" class="param-item">
                <span class="param-key">{{ key }}:</span>
                <span class="param-value">{{ value }}</span>
              </span>
            </div>
          </template>
          <template #cell-notification_config="{ row }">
            <el-tag :type="getNotificationLevelType(row.notification_config?.level)">
              {{ row.notification_config?.level }}
            </el-tag>
          </template>
          <template #cell-is_active="{ row }">
            <span :class="['status-badge', row.is_active ? 'active' : 'inactive']">
              {{ row.is_active ? '启用' : '停用' }}
            </span>
          </template>
          <template #cell-actions="{ row }">
            <button class="action-button" @click="editRule(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4L21.5 5.5z"></path>
              </svg>
              编辑
            </button>
            <button class="action-button action-button-danger" @click="deleteRule(row.id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
              删除
            </button>
          </template>
        </StockListTable>

        <div v-if="alertRules.length === 0 && !loading" class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 2c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
          <p>暂无告警规则</p>
        </div>
      </div>

      <PaginationBar
        v-model:page="pagination.page"
        v-model:page-size="pagination.size"
        :total="alertRules.length"
        :page-sizes="[10, 20, 50, 100]"
        @page-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>

    <DetailDialog
      v-model:visible="showCreateDialog"
      :title="editingRule ? '编辑规则' : '新建规则'"
      @confirm="saveRule"
      @cancel="handleCloseDialog"
    >
      <div class="rule-form">
        <div class="form-row">
          <label class="form-label">规则名称</label>
          <input v-model="ruleForm.rule_name" placeholder="请输入规则名称" class="input" />
        </div>

        <div class="form-row">
          <label class="form-label">股票代码</label>
          <input v-model="ruleForm.symbol" placeholder="请输入股票代码" class="input" />
        </div>

        <div class="form-row">
          <label class="form-label">股票名称</label>
          <input v-model="ruleForm.stock_name" placeholder="请输入股票名称" class="input" />
        </div>

        <div class="form-row">
          <label class="form-label">规则类型</label>
          <select v-model="ruleForm.rule_type" class="select">
            <option v-for="type in ruleTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <div class="form-section">
          <div class="form-section-title">参数配置</div>
          <div class="form-row">
            <label class="form-label">包含ST</label>
            <input type="checkbox" v-model="ruleForm.parameters.include_st" class="checkbox" />
          </div>
          <div class="form-row">
            <label class="form-label">涨跌幅%</label>
            <input v-model="ruleForm.parameters.change_percent_threshold" type="number" placeholder="如: 5" class="input" />
          </div>
          <div class="form-row">
            <label class="form-label">成交量倍数</label>
            <input v-model="ruleForm.parameters.volume_ratio_threshold" type="number" placeholder="如: 2" class="input" />
          </div>
        </div>

        <div class="form-section">
          <div class="form-section-title">通知配置</div>
          <div class="form-row">
            <label class="form-label">通知级别</label>
            <select v-model="ruleForm.notification_config.level" class="select-sm">
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div class="form-row">
            <label class="form-label">通知渠道</label>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="ruleForm.notification_config.channels" value="ui" />
                <span>UI通知</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="ruleForm.notification_config.channels" value="sound" />
                <span>声音</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="ruleForm.notification_config.channels" value="email" />
                <span>邮件</span>
              </label>
            </div>
          </div>
        </div>

        <div class="form-row">
          <label class="form-label">优先级</label>
          <input v-model="ruleForm.priority" type="number" min="1" max="10" class="input" />
        </div>

        <div class="form-row">
          <label class="form-label">是否启用</label>
          <input type="checkbox" v-model="ruleForm.is_active" class="checkbox" />
        </div>
      </div>
    </DetailDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { monitoringApi } from '@/api'
import {
  PageHeader,
  StockListTable,
  PaginationBar,
  DetailDialog
} from '@/components/shared'

import type { TableColumn } from '@/components/shared'

interface AlertRule {
  id: string
  rule_name: string
  symbol: string
  stock_name: string
  rule_type: string
  priority: number
  parameters: Record<string, any>
  notification_config: {
    level: string
    channels: string[]
  }
  is_active: boolean
}

interface RuleForm {
  id: string
  rule_name: string
  symbol: string
  stock_name: string
  rule_type: string
  parameters: {
    include_st: boolean
    change_percent_threshold: number | null
    volume_ratio_threshold: number | null
  }
  notification_config: {
    level: string
    channels: string[]
  }
  priority: number
  is_active: boolean
}

const alertRules = ref<AlertRule[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const editingRule = ref<AlertRule | null>(null)

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const ruleTypes = [
  { value: 'limit_up', label: '涨停监控' },
  { value: 'limit_down', label: '跌停监控' },
  { value: 'volume_spike', label: '成交量激增' },
  { value: 'price_breakthrough', label: '价格突破' },
  { value: 'technical_signal', label: '技术信号' },
  { value: 'news_alert', label: '新闻告警' },
  { value: 'fund_flow', label: '资金流向' }
]

const ruleForm = reactive<RuleForm>({
  id: '',
  rule_name: '',
  symbol: '',
  stock_name: '',
  rule_type: 'limit_up',
  parameters: {
    include_st: false,
    change_percent_threshold: null,
    volume_ratio_threshold: null
  },
  notification_config: {
    level: 'warning',
    channels: ['ui', 'sound']
  },
  priority: 5,
  is_active: true
})

const tableColumns = computed((): TableColumn[] => [
  {
    prop: 'rule_name',
    label: '规则名称',
    width: 150
  },
  {
    prop: 'symbol',
    label: '股票代码',
    width: 120,
    className: 'mono'
  },
  {
    prop: 'stock_name',
    label: '股票名称',
    width: 120
  },
  {
    prop: 'rule_type',
    label: '规则类型',
    width: 120
  },
  {
    prop: 'priority',
    label: '优先级',
    width: 100,
    align: 'right',
    className: 'mono'
  },
  {
    prop: 'parameters',
    label: '参数',
    minWidth: 200
  },
  {
    prop: 'notification_config',
    label: '通知级别',
    width: 120
  },
  {
    prop: 'is_active',
    label: '状态',
    width: 100,
    align: 'center'
  },
  {
    prop: 'actions',
    label: '操作',
    width: 150,
    align: 'center'
  }
])

const paginatedRules = computed(() => {
  const start = (pagination.page - 1) * pagination.size
  const end = start + pagination.size
  return alertRules.value.slice(start, end)
})

const getRuleTypeClass = (type: string): string => {
  switch (type) {
    case 'limit_up':
    case 'limit_down':
      return 'danger'
    case 'volume_spike':
      return 'warning'
    case 'price_breakthrough':
      return 'primary'
    case 'technical_signal':
      return 'success'
    default:
      return 'info'
  }
}

const getRuleTypeTag = (type: string): 'success' | 'warning' | 'danger' | 'info' => {
  switch (type) {
    case 'limit_up':
    case 'limit_down':
      return 'danger'
    case 'volume_spike':
      return 'warning'
    case 'price_breakthrough':
      return 'info'
    case 'technical_signal':
      return 'success'
    default:
      return 'info'
  }
}

const formatRuleType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'limit_up': '涨停监控',
    'limit_down': '跌停监控',
    'volume_spike': '成交量激增',
    'price_breakthrough': '价格突破',
    'technical_signal': '技术信号',
    'news_alert': '新闻告警',
    'fund_flow': '资金流向'
  }
  return typeMap[type] || type
}

const getNotificationLevelClass = (level: string): string => {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

const getNotificationLevelType = (level: string): 'success' | 'warning' | 'danger' | 'info' => {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

const fetchAlertRules = async (): Promise<void> => {
  loading.value = true
  try {
    const response = await monitoringApi.getAlertRules()
    alertRules.value = response.data || []
    pagination.total = alertRules.value.length
  } catch (error) {
    console.error('获取告警规则失败:', error)
    ElMessage.error('获取告警规则失败')
  } finally {
    loading.value = false
  }
}

const editRule = (rule: AlertRule): void => {
  editingRule.value = rule
  Object.assign(ruleForm, {
    ...rule,
    parameters: { ...rule.parameters },
    notification_config: { ...rule.notification_config }
  })
  showCreateDialog.value = true
}

const saveRule = async (): Promise<void> => {
  try {
    if (editingRule.value) {
      await monitoringApi.updateAlertRule(editingRule.value.id, ruleForm)
      ElMessage.success('规则更新成功')
    } else {
      await monitoringApi.createAlertRule(ruleForm)
      ElMessage.success('规则创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    fetchAlertRules()
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存规则失败')
  }
}

const deleteRule = async (id: string): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定要删除此告警规则吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await monitoringApi.deleteAlertRule(id)
    ElMessage.success('规则删除成功')
    fetchAlertRules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除规则失败:', error)
      ElMessage.error('删除规则失败')
    }
  }
}

const resetForm = (): void => {
  Object.assign(ruleForm, {
    id: '',
    rule_name: '',
    symbol: '',
    stock_name: '',
    rule_type: 'limit_up',
    parameters: {
      include_st: false,
      change_percent_threshold: null,
      volume_ratio_threshold: null
    },
    notification_config: {
      level: 'warning',
      channels: ['ui', 'sound']
    },
    priority: 5,
    is_active: true
  })
  editingRule.value = null
}

const handleCloseDialog = (): void => {
  showCreateDialog.value = false
  resetForm()
}

const handleSizeChange = (size: number): void => {
  pagination.size = size
  pagination.page = 1
}

const handleCurrentChange = (page: number): void => {
  pagination.page = page
}

onMounted(() => {
  fetchAlertRules()
})
</script>

<style scoped lang="scss">

  padding: 24px;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  min-height: 100vh;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--gold-dim);
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
    z-index: 1;
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }
}

.card-body {
  padding: 24px;
}

.param-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .param-item {
    font-size: 12px;
    color: var(--text-secondary);

    .param-key {
      font-weight: 600;
      color: var(--gold-primary);
    }
  }
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.active {
    background: rgba(0, 230, 118, 0.1);
    color: var(--fall);
    border: 1px solid var(--fall);
  }

  &.inactive {
    background: rgba(156, 163, 175, 0.1);
    color: var(--text-muted);
    border: 1px solid var(--gold-dim);
  }
}

.action-button {
  padding: 6px 12px;
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid var(--gold-primary);
  background: transparent;
  color: var(--gold-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;

  svg {
    width: 14px;
    height: 14px;
  }

  &:hover {
    background: var(--gold-primary);
    color: var(--bg-primary);
  }

  &.action-button-danger {
    border-color: #f56c6c;
    color: #f56c6c;

    &:hover {
      background: #f56c6c;
      color: var(--bg-primary);
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;

  svg {
    width: 80px;
    height: 80px;
    margin: 0 auto 16px;
    color: var(--gold-muted);
  }

  p {
    font-family: var(--font-body);
    font-size: 14px;
    color: var(--text-muted);
    margin: 0;
  }
}

.button {
  padding: 12px 24px;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  border: 2px solid var(--gold-primary);
  background: transparent;
  color: var(--gold-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;

  svg {
    width: 18px;
    height: 18px;
  }

  &:hover:not(.loading) {
    background: var(--gold-primary);
    color: var(--bg-primary);
  }

  &.loading {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &::before {
    content: '';
    position: absolute;
    top: 4px;
    left: 4px;
    width: 8px;
    height: 8px;
    border-left: 1px solid currentColor;
    border-top: 1px solid currentColor;
  }

  &.button-primary {
    border-color: var(--rise);
    color: var(--rise);

    &::before {
      border-color: var(--rise);
    }

    &:hover:not(.loading) {
      background: var(--rise);
      color: var(--bg-primary);
    }
  }
}

.input,
.select,
.select-sm {
  background: transparent;
  border: none;
  border-bottom: 2px solid var(--gold-dim);
  padding: 10px 0;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-primary);
  width: 100%;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-bottom-color: var(--gold-primary);
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
  }

  &::placeholder {
    color: var(--text-muted);
  }

  option {
    background: var(--bg-card);
    color: var(--text-primary);
  }
}

  width: 20px;
  height: 20px;
  accent-color: var(--gold-primary);
}

.rule-form {
  .form-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;

    .form-label {
      font-family: var(--font-body);
      font-size: 12px;
      color: var(--gold-muted);
      text-transform: uppercase;
      letter-spacing: 2px;
      font-weight: 600;
    }
  }

  .form-section {
    margin: 24px 0;
    padding: 20px;
    background: rgba(212, 175, 55, 0.05);
    border: 1px solid var(--gold-dim);

    .form-section-title {
      font-family: var(--font-display);
      font-size: 14px;
      font-weight: 600;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-bottom: 20px;
    }
  }

  .checkbox-group {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
    }
  }
}

@media (max-width: 768px) {
    padding: 16px;
  }

  .card {
    padding: 15px;
  }
}
</style>
