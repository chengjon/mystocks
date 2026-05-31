<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import { useTradeReconciliation } from './composables/useTradeReconciliation'

const {
  actionMessage,
  accountOptions,
  errorMessage,
  exportResults,
  exporting,
  handleAccountChange,
  hasAccounts,
  hasImportBatch,
  importBatchId,
  importCsv,
  importRowCount,
  importing,
  loading,
  currentSnapshotRequestId,
  currentSnapshotUpdatedAt,
  displayMatchedCount,
  displayMismatchedCount,
  displayMissingBrokerRecordCount,
  pageStatusText,
  pageStatusType,
  refresh,
  resultRows,
  selectedAccountId,
  selectedFileName,
  setSelectedFile,
  sourceType,
  startDate,
  endDate,
  statementRows,
  statementSummary,
} = useTradeReconciliation()

const runtimeMessage = computed(() => {
  if (errorMessage.value) {
    return errorMessage.value
  }
  if (actionMessage.value) {
    return actionMessage.value
  }
  if (importing.value) {
    return '正在标准化导入记录并生成对账结果...'
  }
  if (loading.value) {
    return '正在同步内部账单和对账结果...'
  }
  if (!hasAccounts.value) {
    return '当前暂无可用于对账的内部账单账户。'
  }
  if (!hasImportBatch.value) {
    return '请选择 CSV 文件并发起对账导入。'
  }
  return ''
})

const executionContext = computed(() => {
  const params = new URLSearchParams(window.location.search)
  const accountId = params.get('account_id') || ''
  const orderId = params.get('order_id') || ''
  const bridgeTaskId = params.get('bridge_task_id') || ''

  if (!accountId && !orderId && !bridgeTaskId) {
    return null
  }

  const target = new URLSearchParams()
  if (accountId) {
    target.set('account_id', accountId)
  }
  if (orderId) {
    target.set('order_id', orderId)
  }
  if (bridgeTaskId) {
    target.set('bridge_task_id', bridgeTaskId)
  }

  return {
    accountId,
    orderId,
    bridgeTaskId,
    href: `/trade/execution?${target.toString()}`,
  }
})

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement | null
  const file = input?.files?.[0] ?? null
  setSelectedFile(file)
}

const onAccountChange = async (event: Event) => {
  const value = (event.target as HTMLSelectElement).value
  await handleAccountChange(value)
}
</script>

<template>
  <div class="trade-reconciliation page-enter" data-testid="trade-reconciliation-page">
    <ArtDecoRouteHeader
      title="对账单工作台"
      subtitle="统一查看内部账单、券商 CSV 导入结果和只读差异状态"
      eyebrow="trade reconciliation desk"
      :show-status="true"
      :status-text="pageStatusText"
      :status-type="pageStatusType"
      test-id="trade-reconciliation-header"
      shell-class="hero-shell artdeco-card-shell"
    >
      <template #meta>
        <span>ACCOUNT: {{ selectedAccountId || 'N/A' }}</span>
        <span>REQ_ID: {{ currentSnapshotRequestId || 'N/A' }}</span>
        <span>UPDATED: {{ currentSnapshotUpdatedAt }}</span>
        <span>IMPORT_BATCH: {{ importBatchId || '未导入' }}</span>
        <span>ROWS: {{ importRowCount || 0 }}</span>
      </template>

      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          data-testid="trade-reconciliation-refresh"
          @click="refresh"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新账单
        </ArtDecoButton>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :disabled="!hasImportBatch || exporting"
          :loading="exporting"
          data-testid="reconciliation-export-button"
          @click="exportResults"
        >
          <template #icon>
            <ArtDecoIcon name="download" />
          </template>
          导出 CSV
        </ArtDecoButton>
      </template>
    </ArtDecoRouteHeader>

    <section class="control-shell artdeco-card-shell" data-testid="trade-reconciliation-control-row">
      <div class="control-grid">
        <label class="field">
          <span>对账账户</span>
          <select
            data-testid="reconciliation-account-select"
            :value="selectedAccountId"
            :disabled="!hasAccounts || loading"
            @change="onAccountChange"
          >
            <option
              v-for="account in accountOptions"
              :key="account.value"
              :value="account.value"
            >
              {{ account.label }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>导入来源</span>
          <select
            data-testid="reconciliation-source-select"
            v-model="sourceType"
            :disabled="importing"
          >
            <option value="normalized_template">统一模板</option>
            <option value="miniqmt">miniQMT</option>
          </select>
        </label>

        <label class="field">
          <span>开始日期</span>
          <input v-model="startDate" type="date" :disabled="loading" />
        </label>

        <label class="field">
          <span>结束日期</span>
          <input v-model="endDate" type="date" :disabled="loading" />
        </label>

        <label class="field field--file">
          <span>CSV 文件</span>
          <input
            data-testid="reconciliation-file-input"
            type="file"
            accept=".csv,text/csv"
            :disabled="importing"
            @change="onFileChange"
          />
          <small>{{ selectedFileName || '尚未选择文件' }}</small>
        </label>

        <div class="field field--actions">
          <span>导入执行</span>
          <ArtDecoButton
            variant="solid"
            size="sm"
            data-testid="reconciliation-import-button"
            :disabled="importing"
            :loading="importing"
            @click="importCsv"
          >
            导入并对账
          </ArtDecoButton>
        </div>
      </div>
    </section>

    <section class="stats-strip artdeco-card-shell" data-testid="trade-reconciliation-status-strip">
      <ArtDecoStatCard label="总笔数" :value="statementSummary.totalCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="账单金额" :value="statementSummary.totalAmount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="手续费" :value="statementSummary.totalCommission" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="已匹配" :value="displayMatchedCount" :show-change="false" variant="rise" />
      <ArtDecoStatCard label="差异" :value="displayMismatchedCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="缺少券商记录" :value="displayMissingBrokerRecordCount" :show-change="false" variant="fall" />
    </section>

    <p v-if="runtimeMessage" class="runtime-message" aria-live="polite" data-testid="trade-reconciliation-runtime-state">
      {{ runtimeMessage }}
    </p>

    <section v-if="executionContext" class="execution-context artdeco-card-shell" data-testid="trade-reconciliation-execution-context">
      <span>执行跟踪上下文</span>
      <strong>{{ executionContext.orderId || executionContext.bridgeTaskId || executionContext.accountId }}</strong>
      <a :href="executionContext.href">返回执行跟踪详情</a>
    </section>

    <section class="grid-shell" data-testid="trade-reconciliation-work-area">
      <ArtDecoCard title="内部账单快照" data-testid="trade-reconciliation-statement-panel">
        <div v-if="statementRows.length === 0" class="table-empty">
          暂无内部账单记录。
        </div>
        <div v-else class="statement-table-shell">
          <table class="statement-table">
            <thead>
              <tr>
                <th>证券代码</th>
                <th>方向</th>
                <th>成交时间</th>
                <th>金额</th>
                <th>手续费</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in statementRows" :key="row.tradeId">
                <td>{{ row.symbol }}</td>
                <td>{{ row.direction === 'buy' ? '买入' : row.direction === 'sell' ? '卖出' : row.direction }}</td>
                <td>{{ row.tradeTime.replace('T', ' ') }}</td>
                <td>{{ row.amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
                <td>{{ row.commission.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </ArtDecoCard>

      <ArtDecoCard title="对账结果" data-testid="trade-reconciliation-result-panel">
        <div v-if="resultRows.length === 0" class="table-empty">
          导入完成后将在这里展示只读对账结果。
        </div>
        <div v-else class="statement-table-shell">
          <table class="statement-table">
            <thead>
              <tr>
                <th>证券代码</th>
                <th>方向</th>
                <th>成交时间</th>
                <th>金额</th>
                <th>手续费</th>
                <th>状态</th>
                <th>券商来源</th>
                <th>差异字段</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in resultRows" :key="row.key">
                <td>{{ row.symbol }}</td>
                <td>{{ row.directionText }}</td>
                <td>{{ row.tradeTime }}</td>
                <td>{{ row.amountText }}</td>
                <td>{{ row.commissionText }}</td>
                <td>
                  <span class="status-chip" :class="`status-chip--${row.status}`">{{ row.statusText }}</span>
                </td>
                <td>{{ row.brokerSourceText }}</td>
                <td>{{ row.mismatchSummary }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<style scoped>
.trade-reconciliation {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-shell,
.control-shell,
.stats-strip {
  padding: var(--artdeco-spacing-5);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-compact-sm);
  letter-spacing: 0.04em;
}

.control-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(11.25rem, 1fr));
  gap: var(--artdeco-spacing-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.field span {
  font-size: var(--artdeco-text-compact-sm);
  font-weight: var(--artdeco-font-semibold);
}

.field select,
.field input[type='date'],
.field input[type='file'] {
  min-height: var(--artdeco-spacing-10);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  border: var(--artdeco-spacing-px) solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-lg);
  background: var(--artdeco-bg-elevated);
  color: var(--artdeco-fg-primary);
}

.field small {
  color: var(--artdeco-fg-muted);
}

.field--actions {
  justify-content: flex-end;
}

.runtime-message {
  margin: 0;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border: var(--artdeco-spacing-px) solid var(--ad-chip-border-warning);
  border-radius: var(--artdeco-radius-lg);
  background: var(--ad-chip-bg-warning);
  color: var(--ad-chip-text-warning);
}

.execution-context {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  color: var(--artdeco-fg-primary);
}

.execution-context span {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-compact-sm);
}

.execution-context strong {
  font-family: var(--artdeco-font-data, 'JetBrains Mono', monospace);
  font-size: var(--artdeco-text-compact-sm);
}

.execution-context a {
  color: var(--artdeco-gold-primary);
  font-size: var(--artdeco-text-compact-sm);
}

.grid-shell {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr));
  gap: var(--artdeco-spacing-5);
}

.statement-table-shell {
  overflow-x: auto;
}

.statement-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--artdeco-text-compact-base);
}

.statement-table th,
.statement-table td {
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-2);
  border-bottom: var(--artdeco-spacing-px) solid var(--artdeco-gold-opacity-10);
  text-align: left;
  white-space: nowrap;
}

.table-empty {
  padding: var(--artdeco-spacing-8) var(--artdeco-spacing-0);
  color: var(--artdeco-fg-muted);
}

.status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 5rem;
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-full);
  font-size: var(--artdeco-text-compact-sm);
  font-weight: var(--artdeco-font-semibold);
}

.status-chip--matched {
  background: var(--ad-chip-bg-active);
  color: var(--ad-chip-text-active);
}

.status-chip--mismatched {
  background: var(--ad-chip-bg-warning);
  color: var(--ad-chip-text-warning);
}

.status-chip--missing_broker_record {
  background: var(--ad-chip-bg-loss);
  color: var(--ad-chip-text-loss);
}

@media (max-width: 48rem) {
  .hero-shell,
  .control-shell,
  .stats-strip {
    padding: var(--artdeco-spacing-4);
  }

  .grid-shell {
    grid-template-columns: 1fr;
  }
}
</style>
