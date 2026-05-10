<script setup lang="ts">
import { onMounted } from 'vue'

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
  <div class="ai-batch-workbench page-enter">
    <header class="workbench-header">
      <div>
        <p class="eyebrow">AI batch workbench</p>
        <h1>批量分析</h1>
        <p class="subtitle">统一观察批量回测、批量选股与批量监控任务的运行时证据。</p>
      </div>
      <button class="icon-button" type="button" :disabled="loading" @click="refreshRuntime">
        刷新
      </button>
    </header>

    <section class="status-band" :class="readinessClass">
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
    <p v-if="runtimeMessage" class="runtime-message">{{ runtimeMessage }}</p>

    <main class="workbench-grid">
      <section class="panel">
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
  gap: 16px;
  padding: 24px;
}

.workbench-header,
.status-band,
.panel {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.72);
}

.workbench-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 20px;
  border-radius: 8px;
}

.eyebrow,
.subtitle,
.status-meta,
.panel-heading span,
small,
.safety-copy,
.runtime-message,
dt {
  color: rgba(226, 232, 240, 0.72);
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  font-size: 28px;
  line-height: 1.2;
}

h2 {
  font-size: 16px;
}

.status-band {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
}

.status-band.is-ready {
  border-color: rgba(34, 197, 94, 0.42);
}

.status-label {
  margin-right: 10px;
  color: #86efac;
}

.status-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.workbench-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
  padding: 16px;
  border-radius: 8px;
}

.panel-heading,
.result-row,
dl div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

label {
  display: grid;
  gap: 6px;
  color: rgba(226, 232, 240, 0.86);
}

input,
select,
textarea {
  min-height: 36px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 6px;
  padding: 8px 10px;
  color: #e2e8f0;
  background: rgba(2, 6, 23, 0.72);
}

textarea {
  resize: vertical;
}

button {
  min-height: 36px;
  border: 1px solid rgba(148, 163, 184, 0.32);
  border-radius: 6px;
  color: #e2e8f0;
  background: rgba(30, 41, 59, 0.86);
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.primary-button {
  background: #0f766e;
  border-color: #14b8a6;
}

.task-row {
  display: grid;
  gap: 4px;
  padding: 10px;
  text-align: left;
}

.task-row.active {
  border-color: #38bdf8;
}

dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

dd {
  margin: 0;
  color: #f8fafc;
}

.result-table {
  display: grid;
  gap: 8px;
}

.result-row {
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}

.result-row.header {
  color: rgba(226, 232, 240, 0.72);
}

.empty-state {
  padding: 20px 0;
  color: rgba(226, 232, 240, 0.62);
}

.compact {
  margin-top: auto;
}

@media (max-width: 900px) {
  .workbench-header,
  .status-band {
    flex-direction: column;
  }

  .workbench-grid {
    grid-template-columns: 1fr;
  }
}
</style>
