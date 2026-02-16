<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { monitoringApi } from '@/api/index';
import type { AlertRuleResponse } from '@/api/types/common';

const { loading, lastRequestId, exec } = useArtDecoApi();
const rules = ref<AlertRuleResponse[]>([]);

const fetchRules = async () => {
  const data = await exec(() => monitoringApi.getAlertRules(), {
    errorMsg: '获取风控规则失败'
  });
  if (data) {
    rules.value = data;
  }
};

onMounted(() => {
  fetchRules();
});
</script>

<template>
  <div class="risk-overview-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Risk Management Rules</h2>
      <div class="trace-id" v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</div>
    </div>

    <div class="rules-container" v-loading="loading">
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>RULE NAME</th>
            <th>TYPE</th>
            <th>TARGET</th>
            <th>STATUS</th>
            <th>PRIORITY</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rule in rules" :key="rule.id">
            <td class="rule-name">{{ rule.rule_name }}</td>
            <td><span class="type-tag">{{ rule.rule_type }}</span></td>
            <td>{{ rule.symbol || 'Global' }}</td>
            <td>
              <span :class="['status-dot', rule.is_active ? 'active' : 'inactive']"></span>
              {{ rule.is_active ? 'Active' : 'Disabled' }}
            </td>
            <td class="priority">{{ rule.priority }}</td>
            <td>
              <button class="action-btn">Edit</button>
              <button class="action-btn toggle">{{ rule.is_active ? 'Disable' : 'Enable' }}</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 无数据 -->
      <div v-if="!loading && rules.length === 0" class="empty-placeholder">
        <p>No active risk rules found. Define new rules to protect your portfolio.</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.risk-overview-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
  }

  .trace-id {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
  }
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-body);

  th {
    text-align: left;
    padding: var(--artdeco-spacing-4);
    font-family: var(--font-display);
    color: var(--artdeco-gold-primary);
    border-bottom: 1px solid var(--artdeco-border-default);
    font-size: var(--artdeco-text-sm);
    letter-spacing: 0.1em;
  }

  td {
    padding: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-primary);
    border-bottom: 1px solid rgb(212 175 55 / 10%);
  }

  tr:hover td {
    background: rgb(212 175 55 / 5%);
  }

  .rule-name {
    font-weight: var(--artdeco-font-semibold);
    color: var(--artdeco-gold-light);
  }

  .type-tag {
    background: var(--artdeco-bg-elevated);
    border: 1px solid var(--artdeco-border-default);
    padding: 2px 6px;
    font-size: var(--artdeco-text-xs);
    font-family: var(--font-mono);
  }

  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;

    &.active { background: var(--artdeco-rise); box-shadow: 0 0 8px var(--artdeco-rise); }
    &.inactive { background: var(--artdeco-fg-muted); }
  }

  .priority {
    font-family: var(--font-mono);
  }

  .action-btn {
    background: transparent;
    border: 1px solid var(--artdeco-gold-dim);
    color: var(--artdeco-gold-dim);
    padding: 2px 8px;
    margin-right: 8px;
    cursor: pointer;
    font-size: var(--artdeco-text-xs);
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--artdeco-gold-primary);
      color: var(--artdeco-gold-primary);
    }
    
    &.toggle {
      border-color: var(--artdeco-fg-muted);
      color: var(--artdeco-fg-muted);
      &:hover { border-color: var(--artdeco-fg-primary); color: var(--artdeco-fg-primary); }
    }
  }
}

.empty-placeholder {
  padding: var(--artdeco-spacing-20);
  text-align: center;
  color: var(--artdeco-fg-muted);
  border: 1px dashed var(--artdeco-border-default);
  margin-top: var(--artdeco-spacing-8);
}
</style>
