<template>
  <div class="alert-rules-management">
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
            <ArtDecoBadge :variant="row.is_active ? 'active' : 'neutral'" size="sm">
              {{ row.is_active ? '启用' : '停用' }}
            </ArtDecoBadge>
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
import { ArtDecoBadge } from '@/components/artdeco'
import { useAlertRulesManagement } from './composables/useAlertRulesManagement'

const { alertRules, loading, showCreateDialog, editingRule, pagination, ruleTypes, ruleForm, tableColumns, paginatedRules, getRuleTypeTag, formatRuleType, getNotificationLevelType, fetchAlertRules, editRule, saveRule, deleteRule, handleCloseDialog, handleSizeChange, handleCurrentChange } = useAlertRulesManagement()
</script>

<style scoped lang="scss">
@use "./styles/AlertRulesManagement.scss" as *;
</style>
