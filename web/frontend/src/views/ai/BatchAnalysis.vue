<script setup lang="ts">
import { onMounted } from 'vue'

import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'

import { useBatchAnalysisWorkbench } from './composables/useBatchAnalysisWorkbench'

const {
  loading,
  submitting,
  runtimeStatus,
  tasks,
  selectedTask,
  runtimeMessage,
  symbolInput,
  form,
  readinessLabel,
  readinessClass,
  maxSymbolsLabel,
  refreshRuntime,
  submitTask,
  selectTask,
} = useBatchAnalysisWorkbench()

onMounted(() => {
  void refreshRuntime()
})
</script>

<template>
  <div class="ai-batch-workbench page-enter" data-testid="ai-batch-page">
    <ArtDecoRouteHeader
      title="批量分析"
      subtitle="统一观察批量回测、批量选股与批量监控任务的运行时证据。"
      eyebrow="AI batch workbench"
      test-id="ai-batch-header"
    >
      <template #actions>
      <button
        class="icon-button"
        type="button"
        :disabled="loading"
        data-testid="ai-batch-refresh"
        @click="refreshRuntime"
      >
        刷新
      </button>
      </template>
    </ArtDecoRouteHeader>

    <section class="status-band" :class="readinessClass" data-testid="ai-batch-status-strip">
      <div>
        <span class="status-label">{{ readinessLabel }}</span>
        <strong>{{ runtimeStatus?.runtime_backend || 'runtime_batch_registry' }}</strong>
      </div>
      <div class="status-meta">
        <span>max symbols: {{ maxSymbolsLabel }}</span>
        <span>{{ runtimeStatus?.supported_operations?.length || 0 }} operations</span>
      </div>
    </section>

    <p class="safety-copy">
      Batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.
    </p>
    <p v-if="runtimeMessage" class="runtime-message" data-testid="ai-batch-runtime-message">{{ runtimeMessage }}</p>

    <main class="workbench-grid" data-testid="ai-batch-primary-surface">
      <section class="panel" data-testid="ai-batch-control-lens">
        <div class="panel-heading">
          <h2>任务配置</h2>
          <span>{{ submitting ? '提交中' : '待提交' }}</span>
        </div>
        <label>
          操作类型
          <select v-model="form.operation">
            <option value="batch_screening">批量选股</option>
            <option value="batch_backtest">批量回测</option>
            <option value="batch_monitoring">批量监控</option>
          </select>
        </label>
        <label>
          标的列表
          <textarea v-model="symbolInput" rows="3" />
        </label>
        <label>
          开始日期
          <input v-model="form.start_date" type="date" />
        </label>
        <label>
          结束日期
          <input v-model="form.end_date" type="date" />
        </label>
        <button
          data-testid="batch-analysis-submit"
          class="primary-button"
          type="button"
          :disabled="submitting"
          @click="submitTask"
        >
          提交分析
        </button>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <h2>任务列表</h2>
          <span>{{ tasks.length }} 个任务</span>
        </div>
        <div v-if="tasks.length === 0" class="empty-state">暂无批量分析任务</div>
        <button
          v-for="task in tasks"
          v-else
          :key="task.task_id"
          data-testid="batch-analysis-task-row"
          class="task-row"
          :class="{ active: selectedTask?.task_id === task.task_id }"
          type="button"
          @click="selectTask(task.task_id)"
        >
          <span>{{ task.task_id }}</span>
          <small>{{ task.operation }} · {{ task.status }} · {{ task.summary.total_symbols }} symbols</small>
        </button>
      </section>

      <section class="panel summary-panel">
        <div class="panel-heading">
          <h2>结果摘要</h2>
          <span>{{ selectedTask?.status || 'empty' }}</span>
        </div>
        <dl>
          <div>
            <dt>任务 ID</dt>
            <dd>{{ selectedTask?.task_id || '-' }}</dd>
          </div>
          <div>
            <dt>候选数量</dt>
            <dd>{{ selectedTask?.summary?.candidate_count ?? '-' }}</dd>
          </div>
          <div>
            <dt>平均分</dt>
            <dd>{{ selectedTask?.summary?.average_score ?? '-' }}</dd>
          </div>
          <div>
            <dt>完成标的</dt>
            <dd>{{ selectedTask?.summary?.completed_symbols ?? '-' }}</dd>
          </div>
        </dl>
        <p class="safety-copy compact">
          {{ selectedTask?.safety?.disclaimer || 'Batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.' }}
        </p>
      </section>

      <section class="panel results-panel">
        <div class="panel-heading">
          <h2>标的结果</h2>
          <span>{{ selectedTask?.results?.length || 0 }} rows</span>
        </div>
        <div class="result-table">
          <div class="result-row header">
            <span>标的</span>
            <span>信号</span>
            <span>分数</span>
          </div>
          <div
            v-for="row in selectedTask?.results || []"
            :key="row.symbol"
            data-testid="batch-analysis-result-row"
            class="result-row"
          >
            <span>{{ row.symbol }}</span>
            <span>{{ row.signal }}</span>
            <span>{{ row.score }}</span>
          </div>
          <div v-if="!selectedTask?.results?.length" class="empty-state">暂无结果</div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.ai-batch-workbench {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-6);
}

.status-band,
.panel {
  border: 1px solid var(--artdeco-border-default);
  background: var(--artdeco-bg-card);
}

.status-meta,
.panel-heading span,
small,
.safety-copy,
.runtime-message,
dt {
  color: var(--artdeco-fg-muted);
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  font-size: var(--artdeco-text-3xl);
  line-height: 1.2;
}

h2 {
  font-size: var(--artdeco-text-base);
}

.status-band {
  display: flex;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border-radius: var(--artdeco-radius-md);
}

.status-band.is-ready {
  border-color: var(--artdeco-info);
}

.status-label {
  margin-right: var(--artdeco-spacing-2);
  color: var(--artdeco-info);
}

.status-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
}

.workbench-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.panel {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
  min-width: 0;
  padding: var(--artdeco-spacing-4);
  border-radius: var(--artdeco-radius-md);
}

.panel-heading,
.result-row,
dl div {
  display: flex;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
}

label {
  display: grid;
  gap: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-primary);
}

input,
select,
textarea {
  min-height: var(--artdeco-spacing-10);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  color: var(--artdeco-fg-primary);
  background: var(--artdeco-bg-global);
}

textarea {
  resize: vertical;
}

button {
  min-height: var(--artdeco-spacing-10);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  color: var(--artdeco-fg-primary);
  background: var(--artdeco-bg-elevated);
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.primary-button {
  background: var(--artdeco-gold-opacity-20);
  border-color: var(--artdeco-border-accent);
}

.task-row {
  display: grid;
  gap: var(--artdeco-spacing-1);
  padding: var(--artdeco-spacing-2);
  text-align: left;
}

.task-row.active {
  border-color: var(--artdeco-info);
}

dl {
  display: grid;
  gap: var(--artdeco-spacing-2);
  margin: 0;
}

dd {
  margin: 0;
  color: var(--artdeco-fg-primary);
}

.result-table {
  display: grid;
  gap: var(--artdeco-spacing-2);
}

.result-row {
  align-items: center;
  padding: var(--artdeco-spacing-2) 0;
  border-bottom: 1px solid var(--artdeco-gold-opacity-15);
}

.result-row.header {
  color: var(--artdeco-fg-muted);
}

.empty-state {
  padding: var(--artdeco-spacing-5) 0;
  color: var(--artdeco-fg-subtle);
}

.compact {
  margin-top: auto;
}

@media (max-width: 56.25rem) {
  .status-band {
    flex-direction: column;
  }

  .workbench-grid {
    grid-template-columns: 1fr;
  }
}
</style>
