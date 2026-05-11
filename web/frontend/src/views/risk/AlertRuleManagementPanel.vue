<template>
  <ArtDecoCard title="规则列表" class="table-card" hoverable>
    <div v-if="editable" class="rule-management-toolbar">
      <ArtDecoButton variant="outline" size="sm" @click="openCreateRuleDialog">新建规则</ArtDecoButton>
    </div>
    <p v-if="mutationMessage" class="runtime-message" aria-live="polite">{{ mutationMessage }}</p>
    <div v-if="!loading && hasVerifiedRulesSnapshot && alertRules.length === 0" class="empty-state">暂无风险告警规则。</div>
    <el-table :data="alertRules" stripe :empty-text="rulesEmptyText">
      <el-table-column prop="rule_name" label="规则名" min-width="220" show-overflow-tooltip />
      <el-table-column prop="rule_type" label="规则类型" width="150" />
      <el-table-column prop="symbol" label="标的" width="120" />
      <el-table-column label="启用状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="180">
        <template #default="{ row }">
          <span class="mono">{{ formatTime(row.updated_at || row.created_at) }}</span>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="editable && hasVerifiedRulesSnapshot && alertRules.length > 0" class="rule-action-list">
      <div v-for="rule in alertRules" :key="rule.id || rule.rule_name" class="rule-action-row">
        <span>{{ rule.rule_name || '未命名规则' }}</span>
        <div class="rule-action-buttons">
          <button class="inline-action" :data-test="`alert-rule-edit-${rule.id}`" @click="openEditRuleDialog(rule)">
            编辑
          </button>
          <button class="inline-action inline-action-danger" :data-test="`alert-rule-delete-${rule.id}`" @click="confirmDeleteRule(rule)">
            删除
          </button>
        </div>
      </div>
    </div>
  </ArtDecoCard>

  <section v-if="editable && showRuleDialog" class="rule-dialog artdeco-card-shell" role="dialog" aria-modal="true">
    <div class="rule-dialog-header">
      <h2>{{ editingRuleId ? '编辑告警规则' : '新建告警规则' }}</h2>
      <button class="inline-action" type="button" @click="closeRuleDialog">关闭</button>
    </div>
    <div class="rule-form-grid">
      <label>
        规则名称
        <input v-model="ruleForm.rule_name" data-test="alert-rule-name-input" class="rule-input" />
      </label>
      <label>
        股票代码
        <input v-model="ruleForm.symbol" data-test="alert-rule-symbol-input" class="rule-input" />
      </label>
      <label>
        股票名称
        <input v-model="ruleForm.stock_name" data-test="alert-rule-stock-name-input" class="rule-input" />
      </label>
      <label>
        规则类型
        <select v-model="ruleForm.rule_type" class="rule-input">
          <option value="limit_up">涨停监控</option>
          <option value="limit_down">跌停监控</option>
          <option value="volume_surge">成交量激增</option>
          <option value="price_change">价格变化</option>
          <option value="technical_break">技术突破</option>
          <option value="dragon_tiger">龙虎榜</option>
        </select>
      </label>
      <label>
        涨跌幅阈值
        <input v-model="ruleForm.change_percent_threshold" data-test="alert-rule-change-threshold-input" type="number" class="rule-input" />
      </label>
      <label>
        成交量倍数
        <input v-model="ruleForm.volume_ratio_threshold" data-test="alert-rule-volume-threshold-input" type="number" class="rule-input" />
      </label>
      <label>
        通知级别
        <select v-model="ruleForm.notification_level" class="rule-input">
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="critical">Critical</option>
        </select>
      </label>
      <label>
        优先级
        <input v-model="ruleForm.priority" type="number" min="1" max="10" class="rule-input" />
      </label>
      <label class="rule-checkbox">
        <input v-model="ruleForm.include_st" type="checkbox" />
        包含 ST
      </label>
      <label class="rule-checkbox">
        <input v-model="ruleForm.is_active" type="checkbox" />
        启用规则
      </label>
    </div>
    <div class="rule-dialog-actions">
      <button class="inline-action" type="button" @click="closeRuleDialog">取消</button>
      <button class="inline-action inline-action-primary" data-test="alert-rule-save-button" type="button" @click="emitSaveRule">
        保存规则
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard } from '@/components/artdeco'
import type { AlertRuleResponse } from '@/api/types/common'

interface RuleFormState {
  rule_name: string
  symbol: string
  stock_name: string
  rule_type: string
  include_st: boolean
  change_percent_threshold: string
  volume_ratio_threshold: string
  notification_level: string
  notification_channels: string[]
  priority: number
  is_active: boolean
}

defineProps<{
  alertRules: AlertRuleResponse[]
  editable: boolean
  hasVerifiedRulesSnapshot: boolean
  loading: boolean
  mutationMessage: string
  rulesEmptyText: string
  formatTime: (value?: string) => string
}>()

const emit = defineEmits<{
  createRule: [payload: Record<string, unknown>]
  updateRule: [id: string, payload: Record<string, unknown>]
  deleteRule: [id: string]
}>()

const showRuleDialog = ref(false)
const editingRuleId = ref<string | null>(null)
const defaultRuleForm = (): RuleFormState => ({
  rule_name: '',
  symbol: '',
  stock_name: '',
  rule_type: 'limit_up',
  include_st: false,
  change_percent_threshold: '',
  volume_ratio_threshold: '',
  notification_level: 'warning',
  notification_channels: ['ui'],
  priority: 5,
  is_active: true,
})
const ruleForm = reactive<RuleFormState>(defaultRuleForm())

function resetRuleForm(): void {
  Object.assign(ruleForm, defaultRuleForm())
  editingRuleId.value = null
}

function numberOrNull(value: string): number | null {
  if (value === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function buildRulePayload(): Record<string, unknown> {
  return {
    rule_name: ruleForm.rule_name,
    symbol: ruleForm.symbol,
    stock_name: ruleForm.stock_name,
    rule_type: ruleForm.rule_type,
    parameters: {
      include_st: ruleForm.include_st,
      change_percent_threshold: numberOrNull(ruleForm.change_percent_threshold),
      volume_ratio_threshold: numberOrNull(ruleForm.volume_ratio_threshold),
    },
    notification_config: {
      level: ruleForm.notification_level,
      channels: ruleForm.notification_channels,
    },
    priority: Number(ruleForm.priority) || 5,
    is_active: ruleForm.is_active,
  }
}

function openCreateRuleDialog(): void {
  resetRuleForm()
  showRuleDialog.value = true
}

function openEditRuleDialog(rule: AlertRuleResponse): void {
  const parameters = (rule.parameters || {}) as Record<string, unknown>
  const notificationConfig = (rule.notification_config || {}) as Record<string, unknown>

  Object.assign(ruleForm, {
    rule_name: rule.rule_name || '',
    symbol: rule.symbol || '',
    stock_name: rule.stock_name || '',
    rule_type: rule.rule_type || 'limit_up',
    include_st: Boolean(parameters.include_st),
    change_percent_threshold: parameters.change_percent_threshold == null ? '' : String(parameters.change_percent_threshold),
    volume_ratio_threshold: parameters.volume_ratio_threshold == null ? '' : String(parameters.volume_ratio_threshold),
    notification_level: typeof notificationConfig.level === 'string' ? notificationConfig.level : 'warning',
    notification_channels: Array.isArray(notificationConfig.channels) ? notificationConfig.channels.map(String) : ['ui'],
    priority: typeof rule.priority === 'number' ? rule.priority : 5,
    is_active: rule.is_active !== false,
  })
  editingRuleId.value = rule.id == null ? null : String(rule.id)
  showRuleDialog.value = true
}

function closeRuleDialog(): void {
  showRuleDialog.value = false
  resetRuleForm()
}

function emitSaveRule(): void {
  const payload = buildRulePayload()
  if (editingRuleId.value) {
    emit('updateRule', editingRuleId.value, payload)
    return
  }
  emit('createRule', payload)
}

function confirmDeleteRule(rule: AlertRuleResponse): void {
  if (rule.id == null) return
  if (!window.confirm('确定要删除此告警规则吗？')) return
  emit('deleteRule', String(rule.id))
}
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.rule-management-toolbar,
.rule-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-4);
}

.rule-action-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
  margin-top: var(--artdeco-spacing-4);
}

.rule-action-row,
.rule-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
}

.rule-action-row {
  padding: var(--artdeco-spacing-3);
  border: var(--artdeco-spacing-px) solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  color: var(--artdeco-fg-secondary);
}

.rule-action-buttons {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.inline-action {
  border: var(--artdeco-spacing-px) solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  color: var(--artdeco-fg-secondary);
  background: var(--artdeco-bg-elevated);
  cursor: pointer;
}

.inline-action-primary {
  color: var(--artdeco-bg-primary);
  background: var(--artdeco-gold-primary);
  border-color: var(--artdeco-gold-primary);
}

.inline-action-danger {
  color: var(--artdeco-down);
  border-color: var(--artdeco-down);
}

.rule-dialog {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.rule-dialog-header h2 {
  margin: 0;
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-primary);
}

.rule-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.rule-form-grid label {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.rule-input {
  border: var(--artdeco-spacing-px) solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  color: var(--artdeco-fg-primary);
  background: var(--artdeco-bg-elevated);
}

.rule-checkbox {
  flex-direction: row !important;
  align-items: center;
}

.runtime-message,
.empty-state {
  margin: 0 0 var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.table-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.mono {
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}
</style>
