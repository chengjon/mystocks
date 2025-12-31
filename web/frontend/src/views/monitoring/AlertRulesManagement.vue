<template>
  <div class="alert-rules-management">
    <div class="page-header">
      <h1>🔔 告警规则管理</h1>
      <p class="subtitle">设置和管理股票监控告警规则</p>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建规则
      </el-button>
      <el-button @click="fetchAlertRules">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 规则列表 -->
    <el-card class="rules-card" shadow="hover">
      <el-table
        :data="alertRules"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="rule_name" label="规则名称" width="200" />
        <el-table-column prop="symbol" label="股票代码" width="120" />
        <el-table-column prop="stock_name" label="股票名称" width="150" />
        <el-table-column prop="rule_type" label="规则类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="getRuleTypeTag(row.rule_type)">
              {{ formatRuleType(row.rule_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" sortable />
        <el-table-column prop="parameters" label="参数" width="200">
          <template #default="{ row }">
            <el-popover
              placement="top-start"
              title="参数详情"
              :width="300"
              trigger="hover"
            >
              <template #default>
                <div v-for="(value, key) in row.parameters" :key="key" class="param-item">
                  <span class="param-key">{{ key }}:</span>
                  <span class="param-value">{{ value }}</span>
                </div>
              </template>
              <template #reference>
                <el-tag size="small">查看参数</el-tag>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="notification_config.level" label="通知级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getNotificationLevelTag(row.notification_config?.level)" size="small">
              {{ row.notification_config?.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="toggleRuleStatus(row)"
              :active-value="true"
              :inactive-value="false"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editRule(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRule(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑规则对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingRule ? '编辑规则' : '新建规则'"
      width="600px"
      :before-close="handleCloseDialog"
    >
      <el-form
        :model="ruleForm"
        :rules="ruleFormRules"
        ref="ruleFormRef"
        label-width="120px"
      >
        <el-form-item label="规则名称" prop="rule_name">
          <el-input v-model="ruleForm.rule_name" placeholder="请输入规则名称" />
        </el-form-item>

        <el-form-item label="股票代码" prop="symbol">
          <el-input v-model="ruleForm.symbol" placeholder="请输入股票代码" />
        </el-form-item>

        <el-form-item label="股票名称">
          <el-input v-model="ruleForm.stock_name" placeholder="请输入股票名称" />
        </el-form-item>

        <el-form-item label="规则类型" prop="rule_type">
          <el-select v-model="ruleForm.rule_type" placeholder="请选择规则类型" style="width: 100%">
            <el-option
              v-for="type in ruleTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="参数配置">
          <el-form
            :model="ruleForm.parameters"
            inline
            label-width="80px"
          >
            <el-form-item label="包含ST">
              <el-switch v-model="ruleForm.parameters.include_st" />
            </el-form-item>
            <el-form-item label="涨跌幅%">
              <el-input v-model="ruleForm.parameters.change_percent_threshold" type="number" placeholder="如: 5" />
            </el-form-item>
            <el-form-item label="成交量倍数">
              <el-input v-model="ruleForm.parameters.volume_ratio_threshold" type="number" placeholder="如: 2" />
            </el-form-item>
          </el-form>
        </el-form-item>

        <el-form-item label="通知配置">
          <el-form
            :model="ruleForm.notification_config"
            inline
            label-width="80px"
          >
            <el-form-item label="通知级别">
              <el-select v-model="ruleForm.notification_config.level" style="width: 100px">
                <el-option label="Info" value="info" />
                <el-option label="Warning" value="warning" />
                <el-option label="Error" value="error" />
                <el-option label="Critical" value="critical" />
              </el-select>
            </el-form-item>
            <el-form-item label="通知渠道">
              <el-checkbox-group v-model="ruleForm.notification_config.channels">
                <el-checkbox label="ui">UI通知</el-checkbox>
                <el-checkbox label="sound">声音</el-checkbox>
                <el-checkbox label="email">邮件</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="ruleForm.priority" :min="1" :max="10" />
        </el-form-item>

        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="ruleForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button type="primary" @click="saveRule">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { monitoringApi } from '@/api'
import type { FormInstance, FormRules } from 'element-plus'

interface AlertRuleParameters {
  include_st: boolean
  change_percent_threshold: number | null
  volume_ratio_threshold: number | null
}

interface AlertRuleNotificationConfig {
  level: 'info' | 'warning' | 'error' | 'critical'
  channels: string[]
}

interface AlertRule {
  id: string
  rule_name: string
  symbol: string
  stock_name: string
  rule_type: string
  parameters: AlertRuleParameters
  notification_config: AlertRuleNotificationConfig
  priority: number
  is_active: boolean
}

interface Pagination {
  page: number
  size: number
  total: number
}

interface RuleType {
  value: string
  label: string
}

// 响应式数据
const alertRules = ref<AlertRule[]>([])
const loading = ref<boolean>(false)
const showCreateDialog = ref<boolean>(false)
const editingRule = ref<AlertRule | null>(null)

// 分页数据
const pagination = reactive<Pagination>({
  page: 1,
  size: 10,
  total: 0
})

// 规则类型
const ruleTypes: RuleType[] = [
  { value: 'limit_up', label: '涨停监控' },
  { value: 'limit_down', label: '跌停监控' },
  { value: 'volume_spike', label: '成交量激增' },
  { value: 'price_breakthrough', label: '价格突破' },
  { value: 'technical_signal', label: '技术信号' },
  { value: 'news_alert', label: '新闻告警' },
  { value: 'fund_flow', label: '资金流向' }
]

// 表单数据
const ruleForm = reactive<AlertRule>({
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

// 表单验证规则
const ruleFormRules: FormRules = {
  rule_name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  symbol: [
    { required: true, message: '请输入股票代码', trigger: 'blur' }
  ],
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请输入优先级', trigger: 'blur' }
  ]
}

const ruleFormRef = ref<FormInstance>()

// 获取告警规则列表
const fetchAlertRules = async (): Promise<void> => {
  loading.value = true
  try {
    const response = await monitoringApi.getAlertRules()
    alertRules.value = (response as unknown) as AlertRule[]
    pagination.total = alertRules.value.length
  } catch (error) {
    console.error('获取告警规则失败:', error)
    ElMessage.error('获取告警规则失败')
  } finally {
    loading.value = false
  }
}

// 获取规则类型标签
const getRuleTypeTag = (type: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
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
    case 'news_alert':
      return 'info'
    case 'fund_flow':
      return 'warning'
    default:
      return 'info'
  }
}

// 格式化规则类型显示
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

// 获取通知级别标签
const getNotificationLevelTag = (level: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
      return 'danger'
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

// 编辑规则
const editRule = (rule: AlertRule): void => {
  editingRule.value = rule
  Object.assign(ruleForm, {
    ...rule,
    parameters: { ...rule.parameters },
    notification_config: { ...rule.notification_config }
  })
  showCreateDialog.value = true
}

// 保存规则
const saveRule = async (): Promise<void> => {
  if (!ruleFormRef.value) return

  try {
    await ruleFormRef.value.validate()

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

// 删除规则
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

// 切换规则状态
const toggleRuleStatus = async (rule: AlertRule): Promise<void> => {
  try {
    await monitoringApi.updateAlertRule(rule.id, { is_active: rule.is_active })
    ElMessage.success(`规则已${rule.is_active ? '启用' : '停用'}`)
  } catch (error) {
    console.error('更新规则状态失败:', error)
    rule.is_active = !rule.is_active
    ElMessage.error('更新规则状态失败')
  }
}

// 重置表单
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

// 关闭对话框
const handleCloseDialog = (): void => {
  showCreateDialog.value = false
  resetForm()
}

// 处理分页大小变化
const handleSizeChange = (size: number): void => {
  pagination.size = size
  fetchAlertRules()
}

// 处理当前页变化
const handleCurrentChange = (page: number): void => {
  pagination.page = page
  fetchAlertRules()
}

// 页面加载时获取数据
onMounted(() => {
  fetchAlertRules()
})
</script>

<style scoped lang="scss">
.alert-rules-management {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .actions {
    margin-bottom: 20px;

    .el-button {
      margin-right: 10px;
    }
  }

  .rules-card {
    margin-bottom: 20px;
  }

  .param-item {
    margin: 4px 0;
    display: flex;

    .param-key {
      font-weight: bold;
      margin-right: 8px;
      min-width: 80px;
    }

    .param-value {
      flex: 1;
    }
  }

  .pagination {
    margin-top: 20px;
    text-align: right;
  }

  .dialog-footer {
    .el-button {
      margin-left: 10px;
    }
  }
}
</style>
